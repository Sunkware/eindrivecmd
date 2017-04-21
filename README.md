## eindrivecmd

An ultra-primitive one-file-per-run root-folder-only command line client for OneDrive, based on OneDrive SDK for Python

You'll need [Python](https://www.python.org/) and [OneDrive SDK for Python ](https://github.com/OneDrive/onedrive-sdk-python) to run this one.
It works with OneDrive Personal, and probably doesn't work with Business. Also, uploading files bigger than 100Mb isn't supported.

### Authentication

Sigh. Since this thing saves locally a "session pickle file", which contains some secure data related to account of application's owner, you should register your own application and not rely on someone else's.
To do so, go to [apps.dev.microsoft.com](https://apps.dev.microsoft.com), login using your Microsoft account, and register a new application (perhaps you'll need to add a "native" platform to it). Then get its "Application ID", also called "Client ID". It's a string like "abcd1234-ab12-cd12-ef12-abcdef123456". Let it be "YOUR_CLIENT_ID".

Open "eindrivecmd.py" in a text editor and, in the beginning, put this string into
```
client_id = 'YOUR_CLIENT_ID'
```
Save changes. Now run
```
python eindrivecmd.py --auth
```
It shows some URL. Copy the URL from the console, follow in the browser, login (again) to your Microsoft account and allow the application to have an access to your OneDrive.
You're then redirected to empty page... from address bar, copy the value of the "code" parameter, that is, another string. Insert it to the application's prompt, hit Enter.
The authentication will happen, at last, and the session file, "session.pickle", should appear.

You have to perform this authentication jig only once. Obviously, without authentication the following commands will not work.

### List root folder content

```
python eindrivecmd.py --list
```
or
```
python eindrivecmd.py -l
```

### Upload file to root folder

```
python eindrivecmd.py --upload ./someDir/testfile.dat
```
or
```
python eindrivecmd.py -u ./someDir/testfile.dat
```

If the file exists already, it will be re-uploaded.

### Download file from root folder

```
python eindrivecmd.py --download testfile.dat ./someDir
```
or
```
python eindrivecmd.py -d testfile.dat ./someDir
```

If the file exists already, it will be re-downloaded.

### Remove file from root folder

```
python eindrivecmd.py --remove testfile.dat
```
or
```
python eindrivecmd.py -r testfile.dat
```

In fact, removed file goes to Recycle Bin. If the file doesn't exist, error will not be raised.

### TODO

Access nested folders and multiple items, copying, moving, sharing, ... a lot.

### Why so primitive?

The main purpose of this thing was to add a OneDrive support to [Naamari project](https://sunkware.org/naamari/index.php).
The upload/download/remove functionality for root folder seems to be sufficient... at the moment.
