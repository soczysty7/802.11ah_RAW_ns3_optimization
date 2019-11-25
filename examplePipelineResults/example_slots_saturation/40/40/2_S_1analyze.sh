../analyzebatch.pl \
./2_S_1/ \
config=name,DataMode,payloadsize,nsta,ngroup,nrawslotnum,BeaconInterval,NumOfRpsElements,contentionperrawslot,TrafficString \
stats=edcaqueuelength,totalnumberofdrops,numberofmactxmissedack,numberoftransmissions,NumberOfDroppedPackets,AveragePacketSentReceiveTime,PacketLoss,latency,GoodputKbit,totaldozetime,EnergyRxIdle,EnergyTx \
$@

#../analyzebatch.pl \
#/proj/wall2-ilabt-iminds-be/ns3ah/sensorlarge/ \
#config=name,sensormeasurementsize,nsta,ngroup,nrawslotnum,trafficinterval,apalwaysschedulesfornextslot,contentionperrawslot \
#stats=edcaqueuelength,tcpconnected,totalnumberofdrops,numberofmactxmissedack,numberoftransmissions,NumberOfDroppedPackets,AveragePacketSentReceiveTime,DropTCPTxBufferExceeded,totaldozetime,numberoftcpretransmissions,numberoftcpretransmissionsfromap,NumberOfAPScheduledPacketForNodeInNextSlot
#
