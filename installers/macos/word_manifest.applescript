on run arguments
  set requestedAction to item 1 of arguments
  set manifestPath to item 2 of arguments
  set documentsPath to item 3 of arguments
  tell application "Finder"
    set documentsFolder to POSIX file documentsPath as alias
    if requestedAction is "register" then
      my registerManifest(manifestPath, documentsFolder)
    else if requestedAction is "unregister" then
      my unregisterManifest(documentsFolder)
    else
      error "Unknown Word manifest action"
    end if
  end tell
end run

on registerManifest(manifestPath, documentsFolder)
  set manifestFile to POSIX file manifestPath as alias
  tell application "Finder"
    try
      set wefFolder to get folder "wef" of documentsFolder
    on error
      set wefFolder to make new folder at documentsFolder with properties {name:"wef"}
    end try
    duplicate manifestFile to wefFolder with replacing
  end tell
end registerManifest

on unregisterManifest(documentsFolder)
  tell application "Finder"
    try
      set wefFolder to get folder "wef" of documentsFolder
      try
        delete file "word-researcher.xml" of wefFolder
      end try
    end try
  end tell
end unregisterManifest
