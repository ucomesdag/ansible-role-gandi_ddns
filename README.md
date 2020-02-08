# [gandi_ddns](#gandi_ddns)

Update DNS records trhough Gandi's LiveDNS API.

|GitHub|Version|Ansible Galaxy|Quality|Downloads|
|------|-------|--------------|-------|---------|
|[![github](https://github.com/ucomesdag/ansible-role-gandi_ddns/workflows/Ansible%20Molecule/badge.svg)](https://github.com/ucomesdag/ansible-role-gandi_ddns/actions)|[![Version](https://img.shields.io/github/release/ucomesdag/ansible-role-gandi_ddns.svg)](https://github.com/ucomesdag/ansible-role-gandi_ddns/releases/)|[![role](https://img.shields.io/ansible/role/53578)](https://galaxy.ansible.com/ucomesdag/gandi_ddns)|[![quality](https://img.shields.io/ansible/quality/53578)](https://galaxy.ansible.com/ucomesdag/gandi_ddns)|[![downloads](https://img.shields.io/ansible/role/d/53578)](https://galaxy.ansible.com/ucomesdag/gandi_ddns)|

## [Example Playbook](#example-playbook)

This example is taken from `molecule/resources/converge.yml` and is tested on each push, pull request and release.
```yaml
---
- name: Converge
  hosts: all
  become: yes
  gather_facts: no

  roles:
    - role: ucomesdag.gandi_ddns
```

## [Role Variables](#role-variables)

These variables are set in `defaults/main.yml`:
```yaml
---
# defaults file for gandi_ddns

# The user to use to connect to machines.
gandi_ddns_user: root

# Do you want to wait for the host to be available?
gandi_ddns_wait_for_host: no

# The number of seconds you want to wait during connection test before failing.
gandi_ddns_timeout: 3
```

## [Dependencies](#Ddpendencies)

Overview of role dependencies:

![dependencies](https://raw.githubusercontent.com/ucomesdag/ansible-role-gandi_ddns/png/requirements.png "Dependencies")

## [Requirements](#role-requirements)

- pip packages listed in [requirements.txt](https://github.com/ucomesdag/ansible-role-gandi_ddns/blob/master/requirements.txt).

## [Compatibility](#compatibility)

This role has been tested on these [container images](https://quay.io/user/ucomesdag):

|container  |tags                   |
|-----------|-----------------------|
|alpine     |edge, latest           |
|amazonlinux|latest                 |
|archlinux  |latest                 |
|centos     |latest, stream8        |
|debian     |latest, buster         |
|fedora     |rawhide, latest, 34, 33|
|opensuse   |latest                 |
|rhel       |latest                 |
|rocky      |latest                 |
|rpi-os     |latest                 |
|ubuntu     |jammy, latest, bionic  |

The minimum version of Ansible required is 4.x, tests have been done to:

- The previous version.
- The current version.
- The development version.

See the [Ansible community changelogs](https://docs.ansible.com/ansible/devel/reference_appendices/release_and_maintenance.html#ansible-community-changelogs) for details.

## [Exceptions](#exceptions)

Some variarations of the build matrix do not work. These are the variations and reasons why the build won't work:

| variation                 | reason                 |
|---------------------------|------------------------|
| amazon:latest | Failed to get D-Bus connection: Operation not permitted |


If you find issues, please register them in [GitHub](https://github.com/ucomesdag/ansible-role-gandi_ddns/issues)

## [License](#license)

Apache-2.0
