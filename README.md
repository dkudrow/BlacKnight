# farmcloud
Fault-tolerant cloud management tools for the Farm Cloud project

### ZooKeeper
The current release of Kazoo does not yet support ZooKeeper 3.5's `reconfig` 
client API command. Instead, install this development branch to virtualenv:

    ./bin/pip install git+https://github.com/rgs1/kazoo.git@support-reconfig
    
### That's all for now.
