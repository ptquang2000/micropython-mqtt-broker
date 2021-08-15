import subprocess
import sys

if len(sys.argv) == 1:
  cm = subprocess.run(['cls'] ,shell=True)
  cm = subprocess.run(['env\\Scripts\\activate'] ,shell=True)
  cm = subprocess.run(['ampy', '-p', 'COM3', 'run', 'main.py'], shell=True)
  exit()

if sys.argv[1] == 'putall':
  cm = subprocess.run(['cls'] ,shell=True)
  cm = subprocess.run(['env\\Scripts\\activate'] ,shell=True)
  print('Start uploading')
  cm = subprocess.run(['ampy', '-p', 'COM3', 'put', 'control_packet'],shell=True)
  print('Done upload control_packet')
  cm = subprocess.run(['ampy', '-p', 'COM3', 'put', 'main.py'], shell=True)
  print('Done upload main')
  exit()

if sys.argv[1] == 'all':
  cm = subprocess.run(['cls'] ,shell=True)
  cm = subprocess.run(['env\\Scripts\\activate'] ,shell=True)
  cm = subprocess.run(['ampy', '-p', 'COM3', 'put', 'control_packet'],shell=True)
  print('Done upload control_packet')
  cm = subprocess.run(['ampy', '-p', 'COM3', 'run', 'main.py'], shell=True)
  exit()

if sys.argv[1] == 'get':
  cm = subprocess.run(['env\\Scripts\\activate'] ,shell=True)
  cm = subprocess.run(['ampy', '-p', 'COM3', sys.argv[1], sys.argv[2]], shell=True)
  exit()

if sys.argv[1] == 'rm':
  cm = subprocess.run(['env\\Scripts\\activate'] ,shell=True)
  cm = subprocess.run(['ampy', '-p', 'COM3', sys.argv[1], sys.argv[2]], shell=True)
  exit()

exit()