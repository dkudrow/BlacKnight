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

BlacKnight is built around a few simple abstractions that provide us with a way of describing the state of the appliance.


Roles
^^^^^

The **role** is the basic building block in describing appliance state. A role embodies a type of service (or collection of services) that fails atomically. We say that a role is **represented** by the services that fulfill it. The roles in our toy appliance are:

* ``farmapp`` - VM instance running the FarmApp application
* ``hadoop`` - VM instance running Hadoop
* ``mysql`` - VM instance running a MySQL database server
* ``euca_nc`` - Eucalyptus node controller (component of Eucalyptus cloud manager)
* ``euca_slave`` - backup Eucalyptus head node (component of Eucalyptus cloud manager)

An example of a role is the appliance's database service: a VM instance running a MySQL server. We'll dub this role ``mysql``. If there are two VM instances running MySQL servers, the representation of ``mysql`` is two.

Each role has two components: **start/stop hooks** and **dependencies**. Start and stop hooks can be triggered to increase or decrease the representation of the role respectively. Practically speaking, these hooks are shell commands that can be invoked to start another service that fulfills the role. In the case of ``mysql``, the start hook would be a shell script that starts a new VM instance running a MySQL server and the stop hook would terminate such an instance. The requirement that roles fail atomically stems from the fact that they must be fully controllable through only a start and stop hook. It is up to the appliance creator to ensure that all roles implement fail-stop.

The dependency consists of a list of other roles which must be present in the appliance before *this* role can run. Each dependency is a tuple consisting of a role name and an integer **capacity**. This is because it is not enough simply to know that one role depends on another - the relationship has to be quantified. The capacity indicates how many *dependers* a *dependee* will support. Consider the ``hadoop`` role which consists of a VM instance running Hadoop process:

``hadoop``
    * start hook: ``/opt/hooks/start_hadoop.sh``
    * stop hook: ``/opt/hooks/stop_hadoop.sh``
    * dependencies: ``(euca_nc: 2), (mysql: 10)``

A VM instance has to be resident in Eucalyptus node controller and so the ``hadoop`` depends on ``euca_nc``. Furthermore, the Hadoop process must have access to the database and so ``hadoop`` also depends on ``mysql``. The capacity of ``euca_nc`` to support ``hadoop`` is 2. This means that there can be at most VM instances running Hadoop per node controller in the appliance. Similarly a single MySQL server can support up to 10 Hadoop processes. If we want to start up an 11th Hadoop process, we must start an additional MySQL server to support it.


Appliance State
^^^^^^^^^^^^^^^

We can describe the state of the appliance using the representation of each role. There are a few different appliance states that we are interested in. The first is the **minimum viable appliance**. This is the smallest representation of each role that still yields a functional appliance. The second is the **optimal appliance**. This is the maximum representation of each role, beyond which performance does not increase. Lastly, we need to be able to describe the **current state** of the appliance - i.e. the current representation of each role.

The first two states are determined by the appliance creator in a **specification** file. The specification contains a definition for each role that looks like this:

* rolename
    * start hook
    * stop hook
    * minimum representation
    * maximum representation
    * dependencies

The minimum viable appliance is determined from *minimum representation* and the optimal appliance is determined from *maximum representation* (this field can be left empty which will result in BlacKnight attempting to increase the representation of this role whenever possible).

The current state is determined by performing a census on the active services. This results in a *current representation* for each role.


Diff
^^^^

The diff operation below is used to generate a list of actions to transition between the current state and the state that best approximates the optimal appliance given avaiable hardware. diff is invoked every time a change is detected in the appliance.

The diff occurs in two phases. The first phase brings the appliance to it's minimum viable configuration. If this fails, it is because the appliance lacks the necessary hardware for a the minimum configuration and the appliance fail-stops. If the first phase succeeds, the second phase attempts to bring the appliance to its optimal configuration. If this fails, the appliance simply runs at a degraded state since the minimum viable configuration is guaranteed by the first stage.

Both phases make use of a recursive sub-routine which attempts to increase the representation of a role. The sub-routine traverses a weighted DAG constructedpa from the current state of the appliance. The nodes in the DAG correspond to roles with the node weights indicating the current representation of the role. The edges corresond to dependencies with the edge weights corresponding to the total demand of the dependency (current representation times dependency capacity).

 FIGURE

The sub-routine starts by provisionally increasing the weight of the node and updating the weights of outgoing edges. The node's successor's are then visited and for each the in-degree (sum of weights of incoming edges) is compared to its weight. If the in-degree exceeds the successor's node weight, demand for that role has exceeded supply and it's representation has to be increased. This is done by calling the sub-routine recursively.

The recursion ends when a leaf node is reached. Leaf nodes are roles with no dependencies and have an implicit dependence on a physical host in the appliance. Thus when increasing the representation of a leaf node, we must allocate a physical host to accommodate. If there is an unused physical host, it is allocated. If there is not, we search for a role that contains a surplus (current reprsentation is greater than min representation) and re-purpose one of its hosts. If no host can be allocated, we must abort the whole tree of recursive calls.

Because we cannot know until we reach a leaf node whether the appliance can support increase in representation, all provisional changes are transactional. If we successfully increase the the weight of a leaf node, the changes are committed. Otherwise the changes are aborted.


Implementation
--------------

WRITEME

Developing Appliances
---------------------

WRITEME

cloud manager and primary head node (not role)
responsibilities of roles in assessing their own status
atomicity of roles