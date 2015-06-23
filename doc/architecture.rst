System Architecture
===================


Cloud Software Appliances
-------------------------

Unlike a general purpose cloud, a cloud software appliance (or simply *"appliance"*) is a private cloud that exposes only the APIs of the applications it is hosting. An appliance consists of a small scale private cloud, pre-loaded with a limited set of applications as well as the platform and infrastructure on which they run. You can think of it as a web-service-in-a-box. An appliance is meant to be fully self-contained, operating for long periods of time without an operator. Therefore, it must be able to detect changes to it's configuration (e.g. hardware and software failures) and adjust to make best the best use of existing resources.

To make these concepts a little more concrete, I will refer to the following toy appliance throughout this document:

FIGURE

This appliance is composed of

* four hosts running a Eucalyptus cloud;
* non-user facing utilities (Hadoop, MySQL) running in Eucalyptus VM instances;
* a user facing API (fictional FarmApp web application) running in Eucalyptus VM instances.


Terminology
-----------

Host
    Refers to a physical machine in the appliance.

Service
    Refers to a network-accessible process (or group of processes) that are started and stopped together. This includes infrastructure management (e.g. Eucalyptus node controller), platform tools (e.g. virtual machine instance running a MySQL database) as well as application services (e.g. appliance's user facing API).

Abstractions
------------

BlacKnight is built around a few basic abstractions that provide us with a way of describing the state of the appliance.


Roles
^^^^^

The **role** is the basic building block in describing appliance state. A role represents a type of service (or collection of services) that fails atomically. For instance, the roles in our toy appliance are:

* ``farmapp`` - VM instance running the FarmApp application
* ``hadoop`` - VM instance running Hadoop
* ``mysql`` - VM instance running a MySQL database server
* ``euca_nc`` - Eucalyptus node controller (component of Eucalyptus cloud manager)
* ``euca_slave`` - backup Eucalyptus head node (component of Eucalyptus cloud manager)

We say that a role is **represented** by the services that fulfill it. For instance, if there are two VM instances running MySQL servers, we say that the representation of ``mysql`` is two.

Each role has two components:

#. **Start and stop hooks** - these hooks can be triggered to increase or decrease the representation of the role. Practically speaking these, hooks are shell commands that can be invoked to start another service that fulfills the role. In the case of ``mysql``, the start hook would be a shell script that starts a new VM instance running a MySQL server and the stop hook would terminate such an instance.

#. **Dependencies** - most roles in an appliance interact with other roles. These interactions are described by dependencies. The ``hadoop`` role consists of a Hadoop process running in a VM instance. As such it depends on the ``euca_node_controller`` role to run because VM instance requires a node controller on which to run. Similarly, ``hadoop`` makes use of a database and so it also depends on ``mysql``.

The requirement that roles fail atomically stems from the fact that they must be fully controllable through only a start and stop hook. It is up to the appliance creator to ensure that all roles implement fail-stop.

Appliance State
^^^^^^^^^^^^^^^

We can describe the state of the appliance using the representation of each role. We structure this information as a weighted DAG (the reason for this will become clear when I describe the Diff operation below).


Diff
----

The Diff operation below is used to generate a list of remediating


Developing Appliances
---------------------

responsibilities of roles in assessing their own status
atomicity of roles