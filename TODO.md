# farmcloud
* Come up with a better name than farmcloud...
* Certain roles will not be bound to a particular node. Consider a role for a
 particular instance type. There is no easy way for us to figure out where 
 this instance is running. We need to keep track of these orphan roles.
* Define some sort of role exclusivity. For instance, we shouldn't try to run
 a NC on the same node as a CLC. Some roles should indicate that they cannot 
 share.