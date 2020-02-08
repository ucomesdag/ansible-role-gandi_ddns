#!/usr/bin/env python
# encoding: utf-8
'''
Gandi v5 LiveDNS - DynDNS Update via REST API and CURL/requests

@author: cave
License GPLv3
https://www.gnu.org/licenses/gpl-3.0.html

Created on 13 Aug 2017
http://doc.livedns.gandi.net/ 
http://doc.livedns.gandi.net/#api-endpoint -> https://dns.gandi.net/api/v5/
'''

from __future__ import print_function
import time
import requests, json
import config
import argparse
import netifaces
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def requests_retry_session(
  retries=3,
  backoff_factor=0.3,
  status_forcelist=(500, 502, 504),
  session=None,
):
  session = session or requests.Session()
  retry = Retry(
    total=retries,
    read=retries,
    connect=retries,
    backoff_factor=backoff_factor,
    status_forcelist=status_forcelist,
  )
  adapter = HTTPAdapter(max_retries=retry)
  session.mount('http://', adapter)
  session.mount('https://', adapter)
  return session

def get_dynip(session, ifconfig_provider):
  ''' Helper method to get either IPv4 or IPv6 from an external provider
  '''
  r = session.get(ifconfig_provider, timeout=config.timeout)
  if args.verbose:
    print('Checking dynamic IP :' , r.text.strip('\n'))
  ip = r.text.strip('\n')
  return ip

def get_dynip_v4(session):
  ''' find out own IPv4 at home. This is the dynamic IP which changes more or less frequently
  similar to curl ifconfig.me/ip, see example.config.py for details to ifconfig providers 
  ''' 
  ipv4 = None
  if config.ifconfig4:
    ipv4 = get_dynip(session, config.ifconfig4)
    #Check that the IP has the expected length
    if len(ipv4) < 7 or len(ipv4) > 15:
      print('Error - Ignoring new IPv4 adress with incorrect length:', ipv4)
      ipv4 = None
  return ipv4

def get_interface_ipv6(interface):
  ''' Find ipv6 by listing available IPs on the specified interface
  and excluding the local links
  '''
  try:
    for iface in netifaces.ifaddresses(interface)[netifaces.AF_INET6]:
      ip6 = iface['addr']
      if not ip6.startswith('fe80') and not ip6 == "::1":
        if args.verbose:
          print('Checking IPv6 for interface', interface, ':', ip6)
        return ip6
    return None
  except:
    return None

def get_dynip_v6(session):
  ''' find ou own IPv6. This IP can also change more or less frequently.
  It can be retrieved eitehr from an external provider
  or by listing IPv6 on the specified interfaces
  '''
  ipv6 = None
  if config.interface:
    ipv6 = get_interface_ipv6(config.interface)
  elif config.ifconfig6:
    ipv6 = get_dynip(session, config.ifconfig6)

  #Check that the IP has the expected length
  if ipv6 is not None:
    if len(ipv6) < 4 or len(ipv6) > 39:
      print('Error - Ignoring new IPv6 adress with incorrect length:', ipv6)
      ipv6 = None

  return ipv6

def get_uuid(session, domain):
  ''' 
  find out ZONE UUID from domain
  Info on domain "DOMAIN"
  GET /domains/<DOMAIN>:
    
  '''
  url = config.api_endpoint + '/domains/' + domain
  u = session.get(url, headers={"X-Api-Key":config.api_secret}, timeout=config.timeout)
  json_object = json.loads(u._content)
  if u.status_code == 200:
    return json_object['zone_uuid']
  else:
    if args.dryrun:
      return
    print('Error: HTTP Status Code ', u.status_code, 'when trying to get Zone UUID')
    print(json_object['message'])
    exit()

def get_dnsip(session, uuid, subdomain, record_type):
  ''' find out IP from Subdomain DNS-Record
  List all records with name "NAME" and type "TYPE" in the zone UUID
  GET /zones/<UUID>/records/<NAME>/<TYPE>:
  '''
  try:
    url = config.api_endpoint + '/zones/' + uuid + '/records/' + subdomain + '/' + record_type
    headers = {"X-Api-Key":config.api_secret}
    u = session.get(url, headers=headers, timeout=config.timeout)
    json_object = json.loads(u._content)
    if u.status_code == 200:
      if args.verbose:
        print('Checking IP from DNS Record' , subdomain, ':', json_object['rrset_values'][0])
      return json_object['rrset_values'][0]
    else:
      if args.dryrun:
        return
      print('Error: HTTP Status Code ', u.status_code, 'when trying to get IP from subdomain', subdomain) 
      print(json_object['message'])
      return "-1"
  except:
    return

def update_records(session, uuid, dynIP, subdomain, record_type):
  ''' update DNS Records for Subdomains 
    Change the "NAME"/"TYPE" record from the zone UUID
    PUT /zones/<UUID>/records/<NAME>/<TYPE>:
    curl -X PUT -H "Content-Type: application/json" \
          -H 'X-Api-Key: XXX' \
          -d '{"rrset_ttl": 10800,
             "rrset_values": ["<VALUE>"]}' \
          https://dns.gandi.net/api/v5/zones/<UUID>/records/<NAME>/<TYPE>
  '''
  url = config.api_endpoint+ '/zones/' + uuid + '/records/' + subdomain + '/' + record_type
  payload = {"rrset_ttl": config.ttl, "rrset_values": [dynIP]}
  headers = {"Content-Type": "application/json", "X-Api-Key":config.api_secret}
  u = session.put(url, data=json.dumps(payload), headers=headers, timeout=config.timeout)
  json_object = json.loads(u._content)

  if u.status_code == 201:
    if args.verbose:
      print('Status Code:', u.status_code, ',', json_object['message'], ', IP updated for', subdomain)
    return True
  else:
    print('Error: HTTP Status Code ', u.status_code, 'when trying to update IP from subdomain', subdomain)   
    print(json_object['message'])
    exit()


def update_zone(session, uuid, subdomains, dynIP, record_type, force_update):

  dns_updated = False

  for sub in subdomains:
    #get DNS IP for subdomain
    dnsIP = get_dnsip(session, uuid, sub, record_type)
    
    #compare dynIP and DNS IP
    if dynIP == dnsIP and not force_update:
      if args.verbose:
        print('IP Address Match - no further action for subdomain', sub)
    else:
      if args.dryrun:
        print('Dry-run: DNS Records not modified for subdomain', sub, 'old IP', dnsIP, 'new IP', dynIP)
      else:
        print('Going to update/create the DNS Records for the subdomain', sub, 'old IP', dnsIP, 'new IP', dynIP)
        dns_updated = update_records(session, uuid, dynIP, sub, record_type) or dns_updated

  return dns_updated

def update_domain(session, domain, subdomains, ipv4, ipv6, force_update):

  dns_updated = False

  #get zone ID of domain
  uuid = get_uuid(session, domain)

  if args.verbose:
    print('Updating domain', domain, ', uuid', uuid)

  if ipv4:
    dns_updated = update_zone(session, uuid, subdomains, ipv4, "A", force_update) or dns_updated

  if ipv6:
    dns_updated = update_zone(session, uuid, subdomains, ipv6, "AAAA", force_update) or dns_updated

  return dns_updated

def main(force_update, verbosity, dryrun):

  t0=time.time()

  dns_updated = False

  if verbosity:
    print('verbosity turned on')
    
  if dryrun:
    print('performing a dry-run')

  session = requests_retry_session(retries=config.retries, backoff_factor=config.backoff_factor)
  
  ipv4 = get_dynip_v4(session)
  ipv6 = get_dynip_v6(session)
    
  for domain, subdomains in config.domains.items():
    dns_updated = update_domain(session, domain, subdomains, ipv4, ipv6, force_update) or dns_updated

  t1=time.time()

  if verbosity:
    print('Took', t1 - t0, 'seconds')

  if dns_updated:
    exit(2)
  else:
    exit(0)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', '--verbose', help="increase output verbosity", action="store_true")
  parser.add_argument('-f', '--force', help="force an update/create", action="store_true")
  parser.add_argument('-d', '--dryrun', help="do a dry-run", action="store_true")
  args = parser.parse_args()

  main(args.force, args.verbose, args.dryrun)
