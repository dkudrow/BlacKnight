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
* a user-facing API (fictional FarmApp web application) running in Eucalyptus VM instances.

.. note::

    Jargon at the instersection of distributed systems, networks and graphs is an utter catastrophe. In the interest of clarity I define my terms below and am consistent in their use throughout this document.

    Host
        Refers to a physical machine in the appliance.

    Service
        Refers to a process (or group of processes) accessible over a network via an API.

    Node
        Used as it relates to networks and graphs, synonymous with vertex.

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

BlacKnight is implemented as a client that runs on every host in the appliance. All of the clients participate in a leader election so that any given time only one is active. The leader is responsible for monitoring the appliance, performing the diff and initiating remedial actions (the other clients block until they are elected). ZooKeeper is used to manage all of the distributed aspects of BlacKnight including leader election, service detection, and synchronization. If you are not familiar with ZooKeeper, I'm sorry, the documentation is awful. I'll give a brief description in the box below.

Each service in the appliance is responsible for maintaining a node in a pre-determined location in ZooKeeper (e.g. ``/blacknight/services/<unique_service_id>``). This node is ephemeral so if the service dies, the node disappears. The BlacKnight leader registers a watcher on the parent node (in this case ``/blacknight/services``) which will be called every time there is a change in one of its children. The watcher is responsible for querying the state of the appliance by tallying up all of the service nodes, executing a diff and performing any necessary remedial actions.

.. note::

    For the uninitiated ZooKeeper is essentially a distributed filesysem that guarantees Eric Brewer's C and P and the expense of some A. The basic primitive in ZooKeeper is the *node* (occasionally *z-node*) which is similar to a file. A node can contain data and may have children, which makes it looks an awful lot like your run of the mill filesystem hierarchy. An example of a node is ``/blacknight/args/primary_head``. Each of ``blacknight``, ``args``, and ``primary_head`` is a node (which may or may not contain some data) and the ``/``\ s indicate a parent-child relationship. ZooKeeper has a client-server architecture; there are servers on which nodes are actually stored and clients that can communicate with the servers via a limited API to manipulate and access the nodes. Servers and clients are independent processes and can be arranged in any configuration across a deployment (e.g. multiple servers on one machine, dedicated servers, &c.)

One wrinkle here is that ZooKeeper requires at least half of its servers to be up in order to function. In order to get around this, we make use of a ZooKeeper feature new to release 3.5; the *reconfig* command. Reconfig allows us to re-define the server membership so that we never lose a majority. This is okay beacuse the hosts should fail-stop so if they re-enter the appliance, we simply reconfig to accommodate them. Unfortunately Kazoo (our Python ZooKeeper client) support for reconfig is a bit spotty so this feature will have to wait for a future Kazoo release.


Developing Appliances
---------------------

I'd like to breifly touch on design considerations for the appliance developer. For the most part he or she is unconstrained but there are a few architectural observations that can be made to maximize the effectiveness of BlacKnight.

#. **User facing services should scale linearly.** BlacKnight operates under the assumption that more is better; three FarmApp services should be better than two. The appliance should be designed to scale to higher demand by starting more services. This should be a familiar concept to seasoned cloud application developers.

#. **Services are responsible for assessing their status.** Each service is responsible for registering itself with BlacKnight (by maintaing a ZooKeeper node). This is safe to the extent that an appliance does not run foreign code but does protect an appliance from faulty services. Sevices should be able to monitor themselves, assess their own status and stop themselves if anything goes wrong. A service with degraded performance can limp along and as long as it maintains its node BlacKnight does not differentiate between a degraded service and a healthy one. A service should stop itself if there are problems so that BlacKnight can restart it.

#. **Roles should fail atomically.** The appliance developer is charged with writing the specification and partitioning the appliance into roles. The whole purpose of a role is to define a service unit that can be controlled with a start-stop switch. Consider a role consisting of a service running inside of a VM instance; what if the service stops but the instance persists? Roles should be designed in such a way that all of the functionality they encapsulate can be relied upon to fail atomically.
