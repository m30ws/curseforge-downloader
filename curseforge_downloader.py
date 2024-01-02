# Include mods that are marked as "required":false in manifest.
DOWNLOAD_ONLY_REQUIRED = True

# Display "Downloading..." & "Downloaded." messages for mods
PRINT_DOWNLOAD_PROGRESS = True

# Print what would be downloaded but do not actually download
SIMULATE_DOWNLOADS = False

# ==============================

# curseforge example pack: https://www.curseforge.com/api/v1/mods/876781/files/4951563/download
# forge example link: https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.2.0/forge-1.20.1-47.2.0-installer.jar 

import sys
import os
import json
import re
import zipfile
import shutil

import time

from urllib.request import urlopen, urlretrieve

PREFIX = "* " # "#"

def usage():
	""" """
	return f"usage: {sys.argv[0]} <modpack_zip_file.zip> <additional_curse_mods.json> <additional_mods.json>"


def error(msg, ex=None):
	""" """
	if msg.strip():
		print(f'\n- {msg}')
	if ex is not None:
		print(f'-> {ex}')
	print()


def time_passed(start):
	""" """
	return f"{time.time() - start :.2f}s"


def kplus_copytree(src, dst, symlinks=False, ignore=None):
	""" """
	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			shutil.copytree(s, d, symlinks, ignore)
		else:
			shutil.copy2(s, d)


# def contains_modstoml(fullname):
# 	try:
# 		with zipfile.ZipFile(fullname, "r") as mod_zip:
# 			with mod_zip.open('META-INF/mods.toml') as fp:
# 				# modstoml = fp.read().decode(encoding='utf-8')
# 				return True
# 	except:
# 		return False


def main(file, *args):
	""" """
	print()

	if not file or not file.strip():
		print(usage())
		return -1

	file = os.path.abspath(file)

	if not os.path.isfile(file):
		error(f"Item specified neither a zip nor json manifest file !")
		return -2

	start_time = time.time()

	base, ext = os.path.splitext(os.path.basename(file))

	manifest_file = None

	if ext == '.zip':
		try:
			extract_time = time.time()

			with zipfile.ZipFile(file, 'r') as zip_ref:
				extract_dir = f"{os.path.dirname(file)}/{base}"
				# print(f"edir: {extract_dir}")

				try:
					shutil.rmtree(extract_dir)
					print(f"{PREFIX}Removed directory {extract_dir}/")
				except:
					pass
				try:
					os.mkdir(extract_dir)
					print(f"{PREFIX}Created directory {extract_dir}/")
				except Exception as ex:
					error(f"Cannot create directory (non-fatal; falling back to {extract_dir}/)!", ex)
					return -4

				print(f"{PREFIX}Extracting {file} to {extract_dir}/ ...")
				zip_ref.extractall(extract_dir)

				if 'manifest.json' in os.listdir(extract_dir):
					manifest_file = f"{extract_dir}/manifest.json"
					print(f"{PREFIX}Extracted ... {time_passed(extract_time)}")
				else:
					error(f"Invalid zip, manifest not present !")
					return -5

		except Exception as ex:
			# error(f"Extraction error ! ({ex})")
			error(f"Extraction error !", ex)
			return -6

	elif ext == '.json':
		manifest_file = file

	else:
		error(f"Unknown format !")
		return -7


# Read and parse manifest file
	try:
		with open(f"{manifest_file}", encoding='utf-8') as fp:
			print(f"\n{PREFIX}Manifest file is :: {manifest_file}")
			manifest = json.load(fp)

	except Exception as ex:
		# error(f"Cannot read manifest ! ({ex})")
		error(f"Cannot read manifest file !", ex)
		return -8


# Parse additional mods

	additional_curse_mods = []
	try:
		with open(args[0]) as fp:
			additional_curse_mods = json.load(fp)
	except:
		pass

	additional_mods = []
	try:
		with open(args[1]) as fp:
			additional_mods = json.load(fp)
	except:
		pass


# Remove and re-create output dir

	try:
		out_dir = f"{os.path.dirname(file)}/{manifest['name']} {manifest['version']} Downloaded"
	except Exception as ex:
		error("Invalid manifest", ex)
		return -9

	try:
		shutil.rmtree(f"{out_dir}")
		print(f"{PREFIX}Removed directory {out_dir}/")
	except:
		pass
	try:
		os.mkdir(f"{out_dir}")
		print(f"{PREFIX}Created directory {out_dir}/")
	except Exception as ex:
		out_dir = f"{os.path.dirname(file)}"
		error(f"Cannot create directory (non-fatal; falling back to {out_dir}/)!", ex)

	print(f"\n{PREFIX}Output directory :: {out_dir}/")


	try:
# Generate Forge URL
		forgedl_time = time.time()

		forge_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge"
		# /1.20.1-47.2.0/forge-1.20.1-47.2.0-installer.jar
		
		mc_ver = manifest['minecraft']['version']
		forge_id = manifest['minecraft']['modLoaders'][0]['id'].split('-')[1]
		for ml in manifest['minecraft']['modLoaders']:
			if ml['primary']:
				forge_id = ml['id'].split('-')[1]

		forge_url += f"/{mc_ver}-{forge_id}"
		forge_url += f"/forge-{mc_ver}-{forge_id}-installer.jar"

		# Download Forge

		try:
			print(f"\n{PREFIX}Downloading Forge {mc_ver} {forge_id} ({forge_url}) ...")
			forge_savename = f"{out_dir}/forge-{mc_ver}-{forge_id}-installer.jar"

			if SIMULATE_DOWNLOADS:
				# time.sleep(0.01)
				pass
			else:
				resp = urlretrieve(forge_url, forge_savename)

			print(f"{PREFIX}Done. ({forge_savename}) ... {time_passed(forgedl_time)}")

		except Exception as ex:
			error(f"Error downloading Forge (non-fatal)", ex)

	except Exception as ex:
		error(f"Error generating Forge filename (non-fatal)", ex)

	print()

# Remove and re-create mods dir

	mods_dir = f"{out_dir}/mods"
	try:
		shutil.rmtree(f"{mods_dir}")
		print(f"{PREFIX}Removed directory {mods_dir}/")
	except:
		pass
	try:
		os.mkdir(f"{mods_dir}")
		print(f"{PREFIX}Created directory {mods_dir}/")
	except Exception as ex:
		mods_dir = f"{os.path.dirname(file)}"
		error(f"Cannot create directory (non-fatal; falling back to {mods_dir}/)!", ex)

# Remove and re-create resourcepacks dir

	respacks_dir = f"{out_dir}/resourcepacks"
	try:
		shutil.rmtree(f"{respacks_dir}")
		print(f"{PREFIX}Removed directory {respacks_dir}/")
	except:
		pass
	try:
		os.mkdir(f"{respacks_dir}")
		print(f"{PREFIX}Created directory {respacks_dir}/")
	except Exception as ex:
		respacks_dir = f"{os.path.dirname(file)}"
		error(f"Cannot create directory (non-fatal; falling back to {respacks_dir}/)!", ex)

# Download mods

	done = 0
	total = len(manifest['files']) +len(additional_curse_mods) #+len(additional_mods)
	ratio_s = lambda: f"{done:4d}/{total:4d}"
	mods_totaldl_time = time.time()
	try:
		print(f"\n{PREFIX}Downloading mods ...")
		for mod in manifest['files']+additional_curse_mods: #+additional_mods:

			if not mod['required']:
				if DOWNLOAD_ONLY_REQUIRED:
					continue

			mod_time = time.time()

			# DL
			# "/551894/files/4688940/download"
			mod_url = f"https://www.curseforge.com/api/v1/mods"
			mod_url += f"/{mod['projectID']}/files/{mod['fileID']}"

			if PRINT_DOWNLOAD_PROGRESS: print(f"\n[DL] {mod_url} ...")

			try:
				# Download json info
				with urlopen(mod_url) as resp:
					jsn = resp.read().decode(encoding='utf-8')
				fname = json.loads(jsn)['data']['fileName']

				# Download file
				mod_url += "/download"

				if fname.endswith('.zip'): # and not contains_modstoml(fname):
					mod_savename = f"{respacks_dir}/{fname}"
				else:
					mod_savename = f"{mods_dir}/{fname}"
				
				if SIMULATE_DOWNLOADS:
					# time.sleep(0.01)
					pass
				else:
					resp = urlretrieve(mod_url, mod_savename)

				done += 1
				if PRINT_DOWNLOAD_PROGRESS: print(f"[{ratio_s()}] downloaded. ({mod_savename}) ... {time_passed(mod_time)}")

			except Exception as ex:
				error(f"Error downloading mod (non-fatal)", ex)
				continue

		print(f"{PREFIX}Finished downloading mods ({ratio_s()} successful) ... {time_passed(mods_totaldl_time)}")

	except KeyboardInterrupt:
		print(f"{PREFIX}Download interrupted ({ratio_s()} downloaded) ... {time_passed(mods_totaldl_time)}")

		return 0

	print(f"\n{PREFIX}Copying override folders ...")

# Copy override folders
	override_copy_time = time.time()
	try:

		srcdir = f"{os.path.dirname(manifest_file)}/overrides"
		dstdir = f"{out_dir}"
		print(f"{srcdir} -> {dstdir}/")
		if sys.version_info >= (3, 8):
			# print(f"normal copytree")
			shutil.copytree(srcdir, dstdir, dirs_exist_ok=True)
		else:
			# print(f"kplus budget copytree")
			kplus_copytree(srcdir, dstdir)

		print(f"{PREFIX}Done. ... {time_passed(override_copy_time)}")

	except Exception as ex:
		error(f"Cannot copy override folders! Copy them manually from {srcdir}", ex)
		# return
		pass


## All done.
	print(f"\nFinished all tasks ... {time_passed(start_time)}")


if __name__=='__main__':
	if len(sys.argv) < 2:
		print(usage())
		exit(-1)

	exit(main(*sys.argv[1:]))
