#!/usr/bin/env python3

#
#  Eindrivecmd - an ultra-primitive one-file-per-run root-folder-only command line client for OneDrive
#  Copyright (c) 2017 Sunkware
#  Key FP = 6B6D C8E9 3438 6E9C 3D97  56E5 2CE9 A476 99EF 28F6
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#  ----------------------------------------------------------------
#  WWW:       sunkware.org
#  E-mail:    sunkware@gmail.com
#  ----------------------------------------------------------------
#

import os
import optparse
import onedrivesdk


# Globals
redirect_uri = 'https://login.live.com/oauth20_desktop.srf'

# Go to apps.dev.microsoft.com for some...
client_id = 'YOUR_CLIENT_ID'
client_secret = '' # Looks like it's not needed for 'native' apps...

api_base_url = 'https://api.onedrive.com/v1.0/'
scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

session_filename = "session.pickle"


def main():
	global redirect_uri, client_id, client_secret, api_base_url, scopes, session_filename

	print("Eindrivecmd v0.9")

	op = optparse.OptionParser()
	op.add_option("-a", "--auth", action = "store_true", default = False, dest = "auth", help = "Authenticate the application for access to OneDrive account")
	op.add_option("-d", "--download", action = "store_true", default = False, dest = "download", help = "Download the file from root folder")
	op.add_option("-l", "--list", action = "store_true", default = False, dest = "enlist", help = "List the content of root folder")
	op.add_option("-r", "--remove", action = "store_true", default = False, dest = "remove", help = "Remove the file from root folder")
	op.add_option("-u", "--upload", action = "store_true", default = False, dest = "upload", help = "Upload the file to root folder")
	opts, args = op.parse_args()

	auth = opts.auth
	download = opts.download
	enlist = opts.enlist
	remove = opts.remove
	upload = opts.upload


	actionsnum = int(auth) + int(download) + int(enlist) + int(remove) + int(upload)

	if actionsnum == 0:
		print("No action is specified! Run with --help or -h.")
		return -1

	if actionsnum > 1:
		print("Only one action may be specified!")
		return -2


	# Authentication OR refreshing token

	http_provider = onedrivesdk.HttpProvider()
	auth_provider = onedrivesdk.AuthProvider(http_provider = http_provider, client_id = client_id, scopes = scopes)

	if auth == True:
		client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)

		auth_url = client.auth_provider.get_auth_url(redirect_uri)
		# Ask for the code
		print('Paste this URL into your browser, approve the app\'s access.')
		print('Copy everything in the address bar after "code=", and paste it below.')
		print(auth_url)
		code = input('Paste code here: ').strip()

		client.auth_provider.authenticate(code, redirect_uri, client_secret)

		auth_provider.save_session()

		print("Authentication done, session saved.")
		return 0

	
	try:
		sessionfile = open(session_filename, "r")
	except IOError as err:
		print("Cannot open session file \"" + session_filename + "\"!")
		print("Run with --auth to authenticate.")
		return -3

	sessionfile.close()

	auth_provider.load_session()
	auth_provider.refresh_token()
	client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)


	# Perform the specified action...

	if enlist:
		if len(args) != 0:
			print("No args for this command!")
			return -4

		print("Listing content of root folder...")

		try:
			items = client.item(drive = 'me', id = 'root').children.get()
		except onedrivesdk.error.OneDriveError as err:
			print("Error " + str(err.status_code) + ": " + err.code)
			return -5

		for i in range(len(items)):
			item = items[i]
			if item.folder is not None:
				print("[" + item.name + "]")
			elif item.file is not None:
				print("\"" + item.name + "\"")
			else:
				print("?" + item.name + "?")

		print("Done.")

		return 0


	if upload:
		if len(args) != 1:
			print("Local filepath only must be specified!")
			return -6

		filepath = args[0]
		print("Uploading \"" + filepath + "\"...")

		try:
			tmpfile = open(filepath, "r")
		except IOError as err:
			print("Cannot open local file \"" + filepath + "\"!")
			return -7

		tmpfile.close()

		basename = os.path.basename(filepath)

		try:
			client.item(drive = 'me', id = 'root').children[basename].upload(filepath)
		except onedrivesdk.error.OneDriveError as err:
			print("Error " + str(err.status_code) + ": " + err.code)
			return -8

		print("Done.")

		return 0


	if download:
		if len(args) != 2:
			print("Filename and local dirpath only must be specified!")
			return -9

		filename = args[0]

		dirpath = args[1]
		if not dirpath.endswith("/"):
			dirpath = dirpath + "/"

		print("Downloading \"" + filename + "\" to \"" + dirpath + "\"...")

		try:
			items = client.item(drive = 'me', id = 'root').children.get()
		except onedrivesdk.error.OneDriveError as err:
			print("Error " + str(err.status_code) + ": " + err.code)
			return -10

		file_found = False
		file_id = -1
		for i in range(len(items)):
			if (items[i].file is not None) and (items[i].name == filename):
				file_found = True
				file_id = items[i].id
				break

		if not file_found:
			print("File not found in root folder!")
			return -11

		try:
			client.item(drive = 'me', id = file_id).download(dirpath + filename)
		except onedrivesdk.error.OneDriveError as err:
			print("Error " + str(err.status_code) + ": " + err.code)
			return -12

		print("Done.")

		return 0
	

	if remove:
		if len(args) != 1:
			print("Filename only must be specified!")
			return -13

		filename = args[0]

		print("Removing \"" + filename + "\"...")

		try:
			items = client.item(drive = 'me', id = 'root').children.get()
		except onedrivesdk.error.OneDriveError as err:
			print("Error " + str(err.status_code) + ": " + err.code)
			return -14

		file_found = False
		file_id = -1
		for i in range(len(items)):
			if (items[i].file is not None) and (items[i].name == filename):
				file_found = True
				file_id = items[i].id
				break

		if not file_found:
			print("File not found in root folder.")
			# not error --- "goal of removing" is attained
		else:
			try:
				client.item(drive = 'me', id = file_id).delete()
			except onedrivesdk.error.OneDriveError as err:
				print("Error " + str(err.status_code) + ": " + err.code)
				return -15

		print("Done.")

		return 0


	return 0


main()