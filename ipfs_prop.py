#!/usr/bin/env python3
import requests
import os
import time
from os.path import join, dirname
from dotenv import load_dotenv
from threading import Thread
import argparse

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

###########################################
def addFile(endpoint):
  projectId = os.environ.get("PROJECT_ID")
  projectSecret = os.environ.get("PROJECT_SECRET")

  # The test file contains the endpoint used and the time now
  files = { 'test': (endpoint+" "+str(time.time())) }

  ### ADD FILE TO IPFS AND SAVE THE HASH ###
  try:
    response = requests.post(endpoint + '/api/v0/add',
      files=files,
      auth=(projectId, projectSecret),
      params={'pin':'false'}
    )
  except requests.exceptions.ConnectionError as err:
    print(f'{time.asctime()}: {endpoint}: ConnectionError')
    return(0)
  else:
    if (response.status_code == 200):
      hash = response.text.split(",")[1].split(":")[1].replace('"','')
      print(f'{time.asctime()}: {endpoint} uploaded file: Hash: {hash}')
    else:
      hash = 0
      print(f'{time.asctime()}: {endpoint} uploading file: Error: {response.status_code}')

    return(hash)

###########################################
def gatewayFile(gateway, hash, timeoutSeconds):
  startTimeSeconds = time.time()
  while True:
    url = f'https://{gateway}/ipfs/{hash}'
    # Special case, assume it's an ipfs node running on the localhost...
    if (gateway == '127.0.0.1'):
      url = f'http://{gateway}:8080/ipfs/{hash}'
    
    try:
      response = requests.get(url)
    except requests.exceptions.ConnectionError as err:
      print(f'{time.asctime()}: {gateway}: ConnectionError')
      break
    else:
      if (response.status_code == 200):
        source, timestamp = response.text.split()
        prop_delay = time.time()-float(timestamp)
        print(f'{time.asctime()}: {source} -> {gateway}: {prop_delay:.3f} Seconds')
        break
      else:
        ##print(f'{time.asctime()}: {gateway}: Error: {response.status_code}')
        if (time.time() > startTimeSeconds+timeoutSeconds):
          print(f'{time.asctime()}: {gateway}: Timeout error after: {int(time.time()-startTimeSeconds)} Sec')
          break


###########################################
def main():
  gateways = [
    '127.0.0.1',
    'general.infura-ipfs.io',
    'ipfs.io',
    'cloudflare-ipfs.com',
    'dweb.link',
    ##'ipfs.eternum.io',
    'gateway.pinata.cloud',
    'nftstorage.link',
    ##'ipfs.jpu.jp',
  ]
  parser = argparse.ArgumentParser(description='Test how long a file takes to propagate across the IPFS network.')
  parser.add_argument('endpoint',
    nargs='?',
    default='https://ipfs.infura.io:5001',
    help='URL of IPFS API endpoint to upload test files to (https://ipfs.infura.io:5001 by default)')
  parser.add_argument('-c', metavar='count', default=-1, type=int, help='Number of files to test (default: forever)')
  parser.add_argument('-t', metavar='minutes', default=5, type=int, help='Timeout (Default 5). Note most gateways have a per request timeout of >=1 minute.')
  args = parser.parse_args()

  endpoint = args.endpoint
  count = args.c+1
  timeoutSeconds = args.t * 60

  def notFinished():
    nonlocal count
    if (count==0): return True
    count -= 1
    return count > 0

  while notFinished():
    # Put the file out there
    hash = addFile(endpoint)
    if hash==0: continue

    # Create a thread for each gateway to read the file and time how long it takes to propagate 
    threads = []
    for gateway in gateways:
      t = Thread(target=gatewayFile, args=[gateway, hash, timeoutSeconds], name=gateway)
      threads.append(t)
    
    for x in threads:
      x.start()
    for x in threads:
      x.join()


if __name__ == "__main__":
  main()