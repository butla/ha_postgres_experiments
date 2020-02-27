Requirements
============

Shared Nothing
---------------
Storage failure in a site should not result in all Database nodes being impacted.
Storage failure shall only impact a Database Node

* Can be done with failover of the databases between the sites.


Utilize the capacity with all Database nodes in a site for  High Read/Write throughput
-----------------------------------------------
Application server can read/write to any database node in the cluster.
For e.g. if a single Database server supports 100 Reads and Writes Per second then
if there are 3 Database nodes does it support 300 Reads and writes per second.

* maybe we don't need that performance
* Can be done with Citus. Can Citus send WAL between datacenters?
  Or does every node have a follower?


Upon a Database node failure Application server should detect the failure
-----------------------------------------------
and subsequent Reads and write should be redirected to the healthy database nodes and not to
the faulty one. In this scenario  the reads and writes sent to the faulty node will fail
but will a retry of it by application result in reads and writes being redirected to the
healthy node

* Will be handled by the app


Write in Site 1 should be replicated to Database nodes in Site 2 and Vice versa
-----------------------------------------------------

Can the application control through the write call to database whether it waits for the writes
to happen to a node in the Primary site, replicated to all other nodes within the site and
then replicated to the nodes in other site
OR Application considers write to be successful once the data is written to a node in the
site and then the data is replicated asynchronously to other nodes within the site and across
other site 

* in postgres those settings are done on the database


Monitoring
----------
Can we check if all nodes in the Database have the data in consistent state.
Nodes within site and across the site

* for postgres: https://www.postgresql.org/docs/current/warm-standby.html#STREAMING-REPLICATION-MONITORING



Arguments for not using Oracle
==============================

* you don't need licenses, development and deployments are easier and non-bureaucratic


Notes
=====

https://bravenewgeek.com/you-cannot-have-exactly-once-delivery/
https://www.citusdata.com/blog/2018/02/21/three-approaches-to-postgresql-replication/
http://docs.citusdata.com/en/v9.2/cloud/availability.html
cap theorem
https://docs.oracle.com/cd/B28359_01/server.111/b28281/architectures.htm#g1012375
https://raft.github.io/raft.pdf
https://www.yugabyte.com/yugabyte-db-vs-cockroachdb/
https://docs.yugabyte.com/latest/architecture/2dc-deployments/
CockroachDB documents


Questions
==========

* can we have a single cluster geographically distributed?
    * in yugabyte, only one cluster can be primary, others are read replicas
* what risk are we alleviating by the secondary DC? When was the tower down last time?
  What does it mean when the system goes down? The routing that  ,


Problems
========

* Doing an operation, but becoming cut off from the rest of the world.
  Only with access to our DB nodes.
  We have the latest state, but it can't be written.
    * if we require confirmation on writes it won't be a problem
    * if something was already done to the routers, but we
* DB that was attempted to be written fails, retry should work with a different node
* can Camunda wait for the DB to become available when it can't write the task status?
* things to have in mind with multimaster:
    * can we ensure no write is lost when one cluster goes offline?


Experiment
===========

* consistency check
    * two database clients for two nodes
    * tests:
        * everybody incrementing one int
        * everybody incrementing their own int
    * challenges:
        * break one node at a time
        * break two nodes
        * partition the network
* see how many retries were made in total by the apps
* TODO should show inconsistencies in some setup without waiting for writes
* visualize as a chart of some metric with vertical lines for node failures?
* network partition between the DC? How will it work?
* celery task runs and DB going down?

* maybe do WAL replication in the end?


Outputs
========

* even with single postgres instance we can do a successful write,
  but we'll still get an error because the DB goes down after it writes, but before it responds
* stumbled upon a bug with yugabyte when writing to a single row - https://github.com/YugaByte/yugabyte-db/issues/1233
* Yugabyte seems closer to postgres that cockroach and boasts more performance and simplicity.
* we should test the robustness with empty celery task graphs, and with empty camunda tasks
* yugabyte can fail automatic sync between DCs if there's prolonged network partition
  https://docs.yugabyte.com/latest/architecture/2dc-deployments/#1-initialize-the-producer-and-the-consumer
* All of the databases promise much, but there's always fine print and our own ops work needed
  to maintain two clusters.
* open source docs are better
* According to Cockroach, with Oracle "For inter-site replication, you must use another tool like
  Golden Gate, which does not use a locking mechanism, and can therefore introduce race-like
  anomalies in your data."
* the client shouldn't have the "smarts" to connect to different PSQL servers. It should be done
  through pgpool-II
* thinking that we can use a DB layer with different properties (lower consistency) and that
  it's JUST going to work is naive. We need to concrete experiments and build on that.
* when I killed the master  deployed on digital ocean, the instances were in sync when they died.
  maybe ping to the clients was too big
+------+---------+
| id   | value   |
|------+---------|
| 5    | 0       |
| 6    | 0       |
| 7    | 0       |
| 8    | 0       |
| 9    | 0       |
| 10   | 0       |
| 4    | 490     |
| 3    | 451     |
| 2    | 411     |
| 1    | 452     |
+------+---------+

TODO
====

* do failover with asynchronous replication, show lost records
    * add password verification - people are scanning ports, I don't want them messing with me
* prove that with sychronous WAL the follower is in the same state as the main one
    * have metrics showing query latency and time compared to single instance
* show failover with synchronous WAL replication
* PI on yugabyte / cockroach
* killing instances with yugabyte / cockroach
    * will we have the same off-by-one problem as with local postgres?
* put notes under https://wiki.tvac.bt.co.uk/display/NGMN/Resilient+Design+Considerations
