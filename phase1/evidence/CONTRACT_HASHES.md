# Phase 1.5 contract and installer hashes

Algorithm: SHA-256. Generated **2026-08-02 EDT** with `npm run hashes`.

## Continuation final hashes

Generated after the real Word defect fixes and rerun under Node 24.14.0. These values
supersede the pre-continuation installer hashes preserved below.

| Artifact | Final SHA-256 |
| :--- | :--- |
| `contracts/openapi.json` | `8b6b8e34847705da178f92ce0862e6445518489ea567bfcec9b94d0d06680444` |
| `taskpane/src/generated/client.ts` | `980c708d0229ca287b4f0c17a7fd1e2e7593f0226e697f9207aeb521a8d03a9d` |
| `package-lock.json` | `976715fb79080b6ca9143a718e097b483c2e55b587ad2efce82377f732981b0b` |
| `companion/requirements.lock` | `9dd1e6bdeea37c91341c9614cfc3dd410c1e29f63e442919b38f71c8d1397d15` |
| `manifest/word-researcher.xml` | `2850b5f51967671a474ab9c29f1af2ba5e87079ea5f9b4b8f6b9f8d967c3dd4a` |
| `installers/macos/install.sh` | `96756b9dc8c3218b9178dd14489778be7b731dc1d31f9eb713144da949302a25` |
| `installers/macos/repair.sh` | `a6b57bd5fd868f070c207b3185114daf0522528e42db48e812f0d55e1768303b` |
| `installers/macos/uninstall.sh` | `359ba37014e0685243925e49ea28d59c1864f4aec685ae2c387f71aefbaecee0` |
| `installers/macos/word_manifest.applescript` | `486e9316c59b6a86062de9a98cb5260eac47a758fc5f940383d71dffb7b0fa55` |
| `installers/windows/common.ps1` | `2229ca2f734fd990e3f77e317b643329e0c8fc73da3ae88b7c33574a30a84ad2` |
| `installers/windows/policy.ps1` | `8c92f9030339ba645239892c4c5a1b7c1d22081212c63d58008a80f9836a9e72` |
| `installers/windows/platform.ps1` | `66f5d104e3882a28d8817d89664038ab3889228bebdf41b15d3c9c11a7181a5c` |
| `installers/windows/install.ps1` | `6e0c2f309d3052770e53c19199c2703f6170ee3ee2c5a3d058547a23e040e365` |
| `installers/windows/repair.ps1` | `37f958adebf82b4feefd0b5609093d1f56d6d5d75960590c09272c869dd997de` |
| `installers/windows/uninstall.ps1` | `26b651fd4b20ddef33c2a8f73d1f63c62779d191d92cc222138610e9444440f8` |
| `installers/windows/tests/phase1.tests.ps1` | `d33ee3607a8b95d000478310a841a5b4d0465e34adf8bc3a4db30abf4a58e201` |

Two consecutive contract/client generations produced identical first two hashes.

## Pre-continuation hashes — preserved, superseded where changed

| Artifact | SHA-256 |
| :--- | :--- |
| `contracts/openapi.json` | `8b6b8e34847705da178f92ce0862e6445518489ea567bfcec9b94d0d06680444` |
| `taskpane/src/generated/client.ts` | `980c708d0229ca287b4f0c17a7fd1e2e7593f0226e697f9207aeb521a8d03a9d` |
| `package-lock.json` | `976715fb79080b6ca9143a718e097b483c2e55b587ad2efce82377f732981b0b` |
| `companion/requirements.lock` | `9dd1e6bdeea37c91341c9614cfc3dd410c1e29f63e442919b38f71c8d1397d15` |
| `manifest/word-researcher.xml` | `2850b5f51967671a474ab9c29f1af2ba5e87079ea5f9b4b8f6b9f8d967c3dd4a` |
| `installers/macos/install.sh` | `68fdf382ecdc8319e8546ac8e2da79d5744d2c155b18d81bd566cd2cb041d4f2` |
| `installers/macos/repair.sh` | `0d406d25e5f98347a75976f93787a39b7698a41aad2eebe0b387ab5e473a8a16` |
| `installers/macos/uninstall.sh` | `9d18c8a2071cf12e5388a193fdf5c93fc9568d7a6e73d4ed1a7e0e8d27cc400f` |
| `installers/macos/word_manifest.applescript` | `486e9316c59b6a86062de9a98cb5260eac47a758fc5f940383d71dffb7b0fa55` |
| `installers/windows/common.ps1` | `d18e5823f5b8bd63c1c0c1028b133eff138528be1748a5703d64ff1e911a5a07` |
| `installers/windows/policy.ps1` | `90ebd9f9a8faeaddce05b2f8320c34f9153baeb1ccdee3202c9ffce8874af0d9` |
| `installers/windows/platform.ps1` | `3188d7acecf2b2b4eac67435b3b71823f09ddf33fbe4cfd2ce51f48f747f2f6c` |
| `installers/windows/install.ps1` | `6e0c2f309d3052770e53c19199c2703f6170ee3ee2c5a3d058547a23e040e365` |
| `installers/windows/repair.ps1` | `37f958adebf82b4feefd0b5609093d1f56d6d5d75960590c09272c869dd997de` |
| `installers/windows/uninstall.ps1` | `26b651fd4b20ddef33c2a8f73d1f63c62779d191d92cc222138610e9444440f8` |
| `installers/windows/tests/phase1.tests.ps1` | `070e573c7676cc0e5667bec0802de852bee61e1a5967271849986afa33fcf4b9` |

Two consecutive OpenAPI/client generations produced the same first two hashes. The hash
command is deterministic and reads only the listed tracked source artifacts.
