import ctypes
import os
import secrets
import sys
from collections.abc import Callable, Sequence
from ctypes import wintypes
from typing import Protocol, cast

CREDENTIAL_SERVICE = "WordResearcher.Phase1"
CREDENTIAL_ACCOUNT = "installation-secret"
MINIMUM_SECRET_BYTES = 32


class CredentialStore(Protocol):
    def get(self, service: str, account: str) -> str | None: ...

    def set(self, service: str, account: str, value: str) -> None: ...

    def delete(self, service: str, account: str) -> None: ...


class InstallationSecretService:
    def __init__(self, store: CredentialStore) -> None:
        self._store = store

    def ensure(self) -> bytes:
        existing = self._store.get(CREDENTIAL_SERVICE, CREDENTIAL_ACCOUNT)
        if existing is not None:
            return validate_installation_secret(existing)
        generated = secrets.token_urlsafe(48)
        self._store.set(CREDENTIAL_SERVICE, CREDENTIAL_ACCOUNT, generated)
        return validate_installation_secret(generated)

    def load(self) -> bytes:
        value = self._store.get(CREDENTIAL_SERVICE, CREDENTIAL_ACCOUNT)
        if value is None:
            raise RuntimeError(
                "Installation secret is missing; run the local installer repair command"
            )
        return validate_installation_secret(value)

    def delete(self) -> None:
        self._store.delete(CREDENTIAL_SERVICE, CREDENTIAL_ACCOUNT)


class MacOSKeychainCredentialStore:
    ITEM_NOT_FOUND = -25300
    UTF8_ENCODING = 0x08000100

    def __init__(self) -> None:
        self._security = ctypes.CDLL(
            "/System/Library/Frameworks/Security.framework/Security"
        )
        self._core_foundation = ctypes.CDLL(
            "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        )
        self._configure_functions()
        self._dictionary_key_callbacks = self._callback_address("kCFTypeDictionaryKeyCallBacks")
        self._dictionary_value_callbacks = self._callback_address(
            "kCFTypeDictionaryValueCallBacks"
        )

    def get(self, service: str, account: str) -> str | None:
        query, owned = self._query(service, account, return_data=True)
        result = ctypes.c_void_p()
        status = self._security.SecItemCopyMatching(query, ctypes.byref(result))
        self._release_all([query, *owned])
        if status == self.ITEM_NOT_FOUND:
            return None
        self._require_success(status, "read")
        try:
            return self._copy_data(result).decode()
        finally:
            self._release(result)

    def set(self, service: str, account: str, value: str) -> None:
        if self.get(service, account) is None:
            self._add(service, account, value)
        else:
            self._update(service, account, value)

    def delete(self, service: str, account: str) -> None:
        query, owned = self._query(service, account)
        status = self._security.SecItemDelete(query)
        self._release_all([query, *owned])
        if status == self.ITEM_NOT_FOUND:
            return
        self._require_success(status, "delete")

    def _add(self, service: str, account: str, value: str) -> None:
        attributes, owned = self._attributes(service, account, value)
        status = self._security.SecItemAdd(attributes, None)
        self._release_all([attributes, *owned])
        self._require_success(status, "write")

    def _update(self, service: str, account: str, value: str) -> None:
        query, query_owned = self._query(service, account)
        updates, update_owned = self._value_attributes(value)
        status = self._security.SecItemUpdate(query, updates)
        self._release_all([query, updates, *query_owned, *update_owned])
        self._require_success(status, "update")

    def _query(self, service: str, account: str, return_data: bool = False):
        service_value = self._string(service)
        account_value = self._string(account)
        pairs = [
            (self._constant("kSecClass"), self._constant("kSecClassGenericPassword")),
            (self._constant("kSecAttrService"), service_value),
            (self._constant("kSecAttrAccount"), account_value),
        ]
        if return_data:
            pairs.extend(self._return_data_pairs())
        return self._dictionary(pairs), [service_value, account_value]

    def _attributes(self, service: str, account: str, value: str):
        query, owned = self._query(service, account)
        value_data = self._data(value.encode())
        self._core_foundation.CFDictionarySetValue(
            query, self._constant("kSecValueData"), value_data
        )
        return query, [*owned, value_data]

    def _value_attributes(self, value: str):
        value_data = self._data(value.encode())
        pairs = [(self._constant("kSecValueData"), value_data)]
        return self._dictionary(pairs), [value_data]

    def _return_data_pairs(self) -> list[tuple[int, int]]:
        return [(self._constant("kSecReturnData"), self._cf_constant("kCFBooleanTrue"))]

    def _dictionary(
        self,
        pairs: Sequence[tuple[int, int | ctypes.c_void_p]],
    ) -> ctypes.c_void_p:
        dictionary = self._core_foundation.CFDictionaryCreateMutable(
            None,
            0,
            self._dictionary_key_callbacks,
            self._dictionary_value_callbacks,
        )
        for key, value in pairs:
            self._core_foundation.CFDictionarySetValue(dictionary, key, value)
        return ctypes.c_void_p(dictionary)

    def _string(self, value: str) -> ctypes.c_void_p:
        return ctypes.c_void_p(
            self._core_foundation.CFStringCreateWithCString(
                None, value.encode(), self.UTF8_ENCODING
            )
        )

    def _data(self, value: bytes) -> ctypes.c_void_p:
        buffer = (ctypes.c_uint8 * len(value)).from_buffer_copy(value)
        return ctypes.c_void_p(self._core_foundation.CFDataCreate(None, buffer, len(value)))

    def _copy_data(self, data: ctypes.c_void_p) -> bytes:
        length = self._core_foundation.CFDataGetLength(data)
        pointer = self._core_foundation.CFDataGetBytePtr(data)
        return ctypes.string_at(pointer, length)

    def _constant(self, name: str) -> int:
        return self._require_pointer(ctypes.c_void_p.in_dll(self._security, name).value, name)

    def _cf_constant(self, name: str) -> int:
        value = ctypes.c_void_p.in_dll(self._core_foundation, name).value
        return self._require_pointer(value, name)

    def _require_pointer(self, value: int | None, name: str) -> int:
        if value is None:
            raise RuntimeError(f"macOS security symbol is unavailable: {name}")
        return value

    def _callback_address(self, name: str) -> ctypes.c_void_p:
        symbol = ctypes.c_byte.in_dll(self._core_foundation, name)
        return ctypes.c_void_p(ctypes.addressof(symbol))

    def _release_all(self, values: list[ctypes.c_void_p]) -> None:
        for value in values:
            self._release(value)

    def _release(self, value: ctypes.c_void_p) -> None:
        if value:
            self._core_foundation.CFRelease(value)

    def _require_success(self, status: int, operation: str) -> None:
        if status != 0:
            raise RuntimeError(
                f"macOS Keychain could not {operation} installation material (OSStatus {status})"
            )

    def _configure_functions(self) -> None:
        self._configure_security_functions()
        self._configure_dictionary_functions()
        self._configure_value_functions()

    def _configure_security_functions(self) -> None:
        self._security.SecItemCopyMatching.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self._security.SecItemAdd.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self._security.SecItemUpdate.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self._security.SecItemDelete.argtypes = [ctypes.c_void_p]
        self._security.SecItemCopyMatching.restype = ctypes.c_int32
        self._security.SecItemAdd.restype = ctypes.c_int32
        self._security.SecItemUpdate.restype = ctypes.c_int32
        self._security.SecItemDelete.restype = ctypes.c_int32

    def _configure_dictionary_functions(self) -> None:
        self._core_foundation.CFDictionaryCreateMutable.restype = ctypes.c_void_p
        self._core_foundation.CFDictionaryCreateMutable.argtypes = [
            ctypes.c_void_p,
            ctypes.c_long,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self._core_foundation.CFDictionarySetValue.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]

    def _configure_value_functions(self) -> None:
        self._core_foundation.CFStringCreateWithCString.restype = ctypes.c_void_p
        self._core_foundation.CFStringCreateWithCString.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_uint32,
        ]
        self._core_foundation.CFDataCreate.restype = ctypes.c_void_p
        self._core_foundation.CFDataCreate.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_long,
        ]
        self._core_foundation.CFDataGetLength.restype = ctypes.c_long
        self._core_foundation.CFDataGetLength.argtypes = [ctypes.c_void_p]
        self._core_foundation.CFDataGetBytePtr.restype = ctypes.POINTER(ctypes.c_uint8)
        self._core_foundation.CFDataGetBytePtr.argtypes = [ctypes.c_void_p]
        self._core_foundation.CFRelease.argtypes = [ctypes.c_void_p]


class CredentialW(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


class WindowsCredentialStore:
    GENERIC_CREDENTIAL = 1
    LOCAL_MACHINE_PERSISTENCE = 2
    ELEMENT_NOT_FOUND = 1168

    def __init__(self) -> None:
        windows_dll = getattr(ctypes, "WinDLL", None)
        last_error = getattr(ctypes, "get_last_error", None)
        if windows_dll is None or last_error is None:
            raise RuntimeError("Windows Credential Manager is unavailable")
        self._get_last_error = cast(Callable[[], int], last_error)
        self._advapi32 = windows_dll("Advapi32.dll", use_last_error=True)
        self._configure_functions()

    def get(self, service: str, account: str) -> str | None:
        del account
        credential_pointer = ctypes.POINTER(CredentialW)()
        found = self._advapi32.CredReadW(
            service, self.GENERIC_CREDENTIAL, 0, ctypes.byref(credential_pointer)
        )
        if not found:
            self._raise_or_return_missing("read")
            return None
        try:
            return self._decode_blob(credential_pointer.contents)
        finally:
            self._advapi32.CredFree(credential_pointer)

    def set(self, service: str, account: str, value: str) -> None:
        blob = value.encode("utf-16-le")
        buffer = ctypes.create_string_buffer(blob)
        credential = self._create_credential(service, account, blob, buffer)
        if not self._advapi32.CredWriteW(ctypes.byref(credential), 0):
            raise RuntimeError("Windows Credential Manager rejected the installation secret")

    def delete(self, service: str, account: str) -> None:
        del account
        deleted = self._advapi32.CredDeleteW(service, self.GENERIC_CREDENTIAL, 0)
        if not deleted:
            self._raise_or_return_missing("delete")

    def _raise_or_return_missing(self, operation: str) -> None:
        error_code = self._get_last_error()
        if error_code == self.ELEMENT_NOT_FOUND:
            return
        raise RuntimeError(
            f"Windows Credential Manager could not {operation} installation material "
            f"(WinError {error_code})"
        )

    def _create_credential(
        self,
        service: str,
        account: str,
        blob: bytes,
        buffer: ctypes.Array[ctypes.c_char],
    ) -> CredentialW:
        return CredentialW(
            Type=self.GENERIC_CREDENTIAL,
            TargetName=service,
            CredentialBlobSize=len(blob),
            CredentialBlob=ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte)),
            Persist=self.LOCAL_MACHINE_PERSISTENCE,
            UserName=account,
        )

    def _decode_blob(self, credential: CredentialW) -> str:
        raw = ctypes.string_at(credential.CredentialBlob, credential.CredentialBlobSize)
        return raw.decode("utf-16-le")

    def _configure_functions(self) -> None:
        credential_pointer = ctypes.POINTER(ctypes.POINTER(CredentialW))
        self._advapi32.CredReadW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            credential_pointer,
        ]
        self._advapi32.CredReadW.restype = wintypes.BOOL
        self._advapi32.CredWriteW.argtypes = [ctypes.POINTER(CredentialW), wintypes.DWORD]
        self._advapi32.CredWriteW.restype = wintypes.BOOL
        self._advapi32.CredDeleteW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
        ]
        self._advapi32.CredDeleteW.restype = wintypes.BOOL
        self._advapi32.CredFree.argtypes = [ctypes.c_void_p]


class InMemoryCredentialStore:
    def __init__(self) -> None:
        self._values: dict[tuple[str, str], str] = {}

    def get(self, service: str, account: str) -> str | None:
        return self._values.get((service, account))

    def set(self, service: str, account: str, value: str) -> None:
        self._values[(service, account)] = value

    def delete(self, service: str, account: str) -> None:
        self._values.pop((service, account), None)


def current_credential_store() -> CredentialStore:
    if sys.platform == "darwin":
        return MacOSKeychainCredentialStore()
    if os.name == "nt":
        return WindowsCredentialStore()
    raise RuntimeError("Phase 1 credential storage supports only macOS and Windows")


def validate_installation_secret(value: str) -> bytes:
    encoded = value.encode()
    if len(encoded) < MINIMUM_SECRET_BYTES:
        raise RuntimeError("Installation secret is invalid; reinstall the local companion")
    return encoded
