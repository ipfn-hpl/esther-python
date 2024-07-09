-- MariaDB dump 10.19  Distrib 10.11.6-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: esther_report
-- ------------------------------------------------------
-- Server version	10.11.6-MariaDB-0+deb12u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `complete`
--

DROP TABLE IF EXISTS `complete`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `complete` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `shot` mediumint(8) unsigned NOT NULL,
  `time_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `item_id` mediumint(8) unsigned NOT NULL,
  `complete_status_id` smallint(5) unsigned NOT NULL,
  `notes` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_complete_item` (`item_id`),
  KEY `complete_status_id` (`complete_status_id`),
  CONSTRAINT `complete_ibfk_1` FOREIGN KEY (`complete_status_id`) REFERENCES `complete_status` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_complete_item` FOREIGN KEY (`item_id`) REFERENCES `item` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complete`
--

LOCK TABLES `complete` WRITE;
/*!40000 ALTER TABLE `complete` DISABLE KEYS */;
/*!40000 ALTER TABLE `complete` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `complete_status`
--

DROP TABLE IF EXISTS `complete_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `complete_status` (
  `id` smallint(5) unsigned NOT NULL,
  `status` varchar(128) NOT NULL,
  `short_status` varchar(16) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complete_status`
--

LOCK TABLES `complete_status` WRITE;
/*!40000 ALTER TABLE `complete_status` DISABLE KEYS */;
INSERT INTO `complete_status` VALUES
(0,'No Problem','V'),
(1,'Attention Required!','!'),
(2,'Urgent Repair Required.','X'),
(3,'Not Completed','NOK'),
(255,'ABORT.','XXX');
/*!40000 ALTER TABLE `complete_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `day_phase`
--

DROP TABLE IF EXISTS `day_phase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `day_phase` (
  `id` smallint(5) unsigned NOT NULL,
  `name` varchar(100) NOT NULL,
  `short_name` varchar(16) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `day_phase`
--

LOCK TABLES `day_phase` WRITE;
/*!40000 ALTER TABLE `day_phase` DISABLE KEYS */;
INSERT INTO `day_phase` VALUES
(0,'Beginning of the Experimental Run (One or Multiple Shots)','StartOfDay'),
(1,'Each Shot','Shot'),
(2,'End of the Experimental Run','EndOfDay');
/*!40000 ALTER TABLE `day_phase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item`
--

DROP TABLE IF EXISTS `item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `item` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `subsystem_id` smallint(5) unsigned NOT NULL,
  `day_phase_id` smallint(5) unsigned NOT NULL,
  `role_id` smallint(5) unsigned NOT NULL,
  `seq_order` smallint(5) unsigned NOT NULL,
  `name` varchar(512) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_item_subsystem` (`subsystem_id`),
  KEY `fk_item_day_phase` (`day_phase_id`),
  KEY `fk_item_role` (`role_id`),
  CONSTRAINT `fk_item_day_phase` FOREIGN KEY (`day_phase_id`) REFERENCES `day_phase` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_item_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_item_subsystem` FOREIGN KEY (`subsystem_id`) REFERENCES `subsystem` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=87 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item`
--

LOCK TABLES `item` WRITE;
/*!40000 ALTER TABLE `item` DISABLE KEYS */;
INSERT INTO `item` VALUES
(1,0,0,1,5,'Initiate Shot'),
(3,0,0,0,10,'Ensure gas supplies (for the Driver and the Test Gases) are OFF'),
(4,0,0,0,20,'Ensure mechanical operator to wear proper PPE'),
(5,0,0,0,30,'Ensure every safety systems are ON and OK (fire alarm, emergency lighting, gas detection…)'),
(6,0,0,0,40,'Ensure UPS of control room is ON, supplying computers, control panel and gas detection system. Ensure that the PLC control systems (in the control room and the experimental hall rack) are ON'),
(7,0,0,0,50,'All doors to remain unlocked as normal for fire escape/access'),
(8,0,0,1,55,'Turn ON necessary electrical equipment (computers, oscilloscopes, etc...)'),
(9,0,1,1,60,'Make a realistic assessment on whether the test can be completed within the imparted time (e. g. if it is 16:00 maybe it is not a good idea to start a test if you plan to leave at 17:00).'),
(10,0,1,0,70,'Agree and sign the global shot setup parameters sheet (driver, compression tube, and test section gas fillings, vacuum parameters, diagnostics, etc…). Ensure parameters are nominal for shot and all equipment is in good condition. Two signatures are needed in the compliance form.'),
(11,0,1,0,80,'Ensure that at least one researcher and the chief engineer are present during the test, one to remain in control room throughout.'),
(12,0,1,0,90,'Undertake CC cleaning (if necessary) and CT and ST cleaning. Perform hardware inspection. Place diaphragm of appropriate sizes in the CC-CT, CT-ST, and ST-DT sections for the planned shot.'),
(13,0,1,0,100,'Ensure there is no leaks of hydraulic fluid. Undertake hydraulic closure procedure for the CC-CT, CT-ST, and ST-DT sections (See Procedimento HPL-012020).'),
(14,0,1,1,110,'Initiate Vacuum Procedure.'),
(15,0,1,1,120,'After the necessary time (experiment-dependent), initiate Combustion Driver procedure.'),
(16,0,1,1,130,'After Vacuum procedure concludes, initiate Test Gas Filling procedure.'),
(17,0,1,1,140,'After shot is concluded, ensure that all the relevant data (pressures, diagnostics, etc…) are recorded, and that pressure inside the chamber (measured in the Dump Tank station is around atmospheric pressure, accounting for the sensor noise. '),
(18,0,1,1,150,'Allow for additional 5min wait time for safety reasons.'),
(19,0,1,1,160,'Turn ON the water cooling circuit pump. Turn ON the ST primary pump to vent out any leftover Helium and Water Vapour. When pressure is lower than 100mbar, turn OFF the ST primary pump. Turn OFF the water cooling circuit pump.'),
(20,0,1,1,170,'Undertake hydraulic opening procedure (See Procedimento HPL-012020).'),
(21,0,1,0,180,'Purge condensed water from the Dump Tank.'),
(22,0,1,0,190,'Remove the burst-ed CC-CT, CT-ST, and ST-DT diaphragms.'),
(23,0,1,0,200,'Check mechanical parts for damage, record for future maintenance.'),
(24,0,1,0,210,'Sign test report with this form attached. End of test.'),
(25,0,2,0,300,'Turn OFF relevant electrical equipment (computers, oscilloscopes, etc…).'),
(26,0,2,0,310,'General cross-check of the experimental hall, control room, and compressor room for any anomalies.'),
(28,0,1,1,210,'Sign test report with this form attached. End of test.'),
(29,0,1,1,80,'Ensure that at least one researcher and the chief engineer are present during the test, one to remain in control room throughout.'),
(30,0,1,1,70,'Agree and sign the global shot setup parameters sheet (driver, compression tube, and test section gas fillings, vacuum parameters, diagnostics, etc…). Ensure parameters are nominal for shot and all equipment is in good condition. Two signatures are needed in the compliance form.'),
(31,1,1,0,10,'Verify that all other general and subsystem safety conditions are met (see Master checklist)'),
(32,2,1,1,20,'Verify that all the sections of the shock-tube (CC-CT, CT-ST, ST-DT) are CLOSED with a diaphragm inside, and pressurized to the preset values in each station. Report the hydraulic pressure in each section.'),
(33,1,1,0,20,'Disable electrical supplies to all non-ATEX electrical equipment in the ATEX area'),
(34,1,1,0,30,'Ensure all doors and gate from experimental hall are CLOSED'),
(35,1,1,0,40,'Place the recoil dampening bags (Aluminium bullet bags) in contact with the rear of the combustion chamber. Ensure these do not block the laser optical path.'),
(36,1,1,0,50,'Turn ON laser ignition system'),
(37,1,1,0,60,'Check for lack of human presence in the gas compressor room and CLOSE door'),
(38,1,1,0,70,'Leave experimental hall and make visual check and audible warning'),
(41,1,1,0,80,'CLOSE control room/lab door'),
(42,1,1,0,90,'OPEN gas storage doors; Turn ON gas supplies; CLOSE and LOCK gas storage doors'),
(43,1,1,1,90,'Log in to control console'),
(44,1,1,1,100,'Enter normalized parameters from log sheet'),
(45,1,1,1,110,'Turn on Kistler & start archive engine'),
(46,1,1,1,120,'Initiate filling sequence'),
(47,1,1,1,130,'Record the partial filling pressures'),
(48,1,1,1,140,'Check that fill is nominal and that the correct final pressure has been reached'),
(49,1,1,1,150,'Check that CC is properly insulated from the piping system (Maximator valves closed)'),
(50,1,1,1,160,'Ensure that the Vacuum and test gas filling procedures have concluded successfully and that the shock-detection and diagnostic systems are ready for recording the shot and waiting for the triggers recorded at shock wave passage'),
(51,1,1,1,170,'Prepare the Kistler gauge system to record the ignition sequence; program all the necessary triggers (oscilloscopes, acquisition cards, etc...), start the laser flash lamp'),
(52,1,1,1,180,'Fire the laser ignition system'),
(53,1,1,1,190,'Record full pressures and volumes on log'),
(54,1,1,1,200,'Set control system to idle'),
(55,1,1,0,210,'Open gas storage doors; Turn OFF gas supplies; Close and lock gas storage doors'),
(56,1,1,0,220,'Enter lab and open doors. Perform a visual inspection'),
(57,1,1,0,230,'Turn OFF laser ignition system and remove the recoil dampening bags. '),
(58,2,1,0,10,'Verify that all other general and subsystem safety conditions are met (see Master checklist)'),
(59,2,1,1,30,'Turn ON the water cooling pump and check that the water is running inside the closed circuit'),
(60,2,1,1,40,'Turn ON the two turbomolecular pump fans'),
(61,2,1,1,50,'Turn ON the two turbomolecular pump controllers and ensure that the pumps are levitating nominally without any error messages'),
(62,2,1,1,60,'Ensure that the two ST gate valves are OPEN and that the two mechanical arms are in the OPEN position'),
(63,2,1,1,70,'Ensure that all the pressure sensors (1x CT, 2x ST, and 2x DT) are ON (turn then ON when required)'),
(64,2,1,1,80,'Ensure that the CT ball valve is in the pump <-> CT section position and that the DT ball valve is in the pump <-> DT section position'),
(65,2,1,1,90,'Ensure that all the control software is ON (boot it as needed) and that the archive engine is active'),
(66,2,1,1,100,'Turn ON the DT primary pump'),
(67,2,1,1,110,'After XXX seconds turn ON the CT primary pump'),
(69,2,1,1,120,'After XXX seconds turn ON the ST primary pump'),
(70,2,1,1,130,'After XXX seconds, ensure that the CT massflow controller is in the CLOSED position, then  switch the CT ball valve to the gas-filling system <-> CT section position, wait YYY seconds, and switch back to the pump <-> CT section position, to purge the CT gas lines downstream of the massflow controller'),
(71,2,1,1,140,'After pressure in the ST section falls in the 1e-1 mbar range, start the acceleration of both ST turbomolecular pumps'),
(72,2,1,1,150,'When the required pressures in all the sections (CT, ST, DT) are met, CLOSE the two ST gate valves, switch the CT ball valve to the gas-filling system <-> CT section position, and switch the DT ball valve to the purge line <-> DT section position'),
(73,2,1,1,160,'After 5min, OPEN the two ST gate valves, and switch back the ball valves to the pump <-> CT section and pump <-> DT section positions'),
(74,2,1,1,170,'After 5min, CLOSE the two ST gate valves, and switch the ball valves to the gas-filling system <-> CT section and vent line <-> DT section positions'),
(75,2,1,1,180,'Give the OK signal for initiating test gas filling'),
(76,2,1,1,190,'Start the deceleration of both ST turbomolecular pumps'),
(77,2,1,1,200,'Turn OFF the CT and DT primary pumps'),
(78,2,1,1,210,'Once the ST turbomolecular pumps return to the levitation position (0 rpm), turn OFF the ST primary pump'),
(79,2,1,1,220,'Turn OFF the two turbomolecular pump controllers'),
(80,2,1,1,230,'Turn OFF the two turbomolecular pump fans'),
(82,2,1,1,240,'Turn OFF the water cooling circuit pump'),
(83,2,1,0,250,'Verify subsystem safety conditions'),
(84,3,1,0,10,'Verify that all other general and subsystem safety conditions are met (see Master checklist)'),
(85,3,1,1,20,'Wait for the OK signal from the Vacuum system for initiating test gas filling'),
(86,4,1,0,10,'Verify that all other general and subsystem safety conditions are met (see Master checklist)');
/*!40000 ALTER TABLE `item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `operator`
--

DROP TABLE IF EXISTS `operator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `operator` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `operator`
--

LOCK TABLES `operator` WRITE;
/*!40000 ALTER TABLE `operator` DISABLE KEYS */;
INSERT INTO `operator` VALUES
(1,'Mário Lino da Silva'),
(2,'Bernardo Carvalho'),
(3,'Rafael Rodrigues');
/*!40000 ALTER TABLE `operator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `precedence`
--

DROP TABLE IF EXISTS `precedence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `precedence` (
  `item_id` mediumint(8) unsigned NOT NULL,
  `after_item_id` mediumint(8) unsigned NOT NULL,
  `min_status` smallint(5) unsigned NOT NULL,
  PRIMARY KEY (`item_id`,`after_item_id`),
  KEY `fk_precedence_after_item` (`after_item_id`),
  CONSTRAINT `fk_precedence_after_item` FOREIGN KEY (`after_item_id`) REFERENCES `item` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_precedence_item` FOREIGN KEY (`item_id`) REFERENCES `item` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `precedence`
--

LOCK TABLES `precedence` WRITE;
/*!40000 ALTER TABLE `precedence` DISABLE KEYS */;
INSERT INTO `precedence` VALUES
(3,1,1),
(4,3,0),
(5,4,0),
(6,5,0),
(7,6,0),
(8,7,0),
(9,7,0),
(9,8,0),
(10,7,0),
(10,9,0),
(11,10,0),
(11,30,0),
(12,11,0),
(12,29,0),
(13,12,0),
(14,13,0),
(15,14,0),
(16,15,0),
(17,16,0),
(17,55,0),
(18,17,0),
(19,18,0),
(20,19,0),
(21,20,0),
(22,21,0),
(23,22,0),
(24,23,0),
(26,25,0),
(28,23,0),
(29,10,0),
(29,30,0),
(30,10,0),
(31,8,0),
(31,16,0),
(32,13,0),
(33,31,0),
(34,33,0),
(35,34,0),
(36,35,0),
(37,36,0),
(38,37,0),
(41,38,0),
(42,41,0),
(43,42,0),
(44,43,0),
(45,44,0),
(46,45,0),
(47,46,0),
(48,47,0),
(49,48,0),
(50,49,0),
(51,50,0),
(52,51,0),
(53,52,0),
(54,53,0),
(55,54,0),
(56,55,0),
(57,56,0),
(58,13,0),
(59,32,0),
(59,58,0),
(60,32,0),
(61,32,0),
(62,59,0),
(62,60,0),
(62,61,0),
(63,62,0),
(64,63,0),
(65,64,0),
(66,65,0),
(67,66,0),
(70,69,0),
(71,70,0),
(72,71,0),
(73,72,0),
(74,73,0),
(75,74,0),
(76,75,0),
(77,76,0),
(78,77,0),
(79,78,0),
(80,79,0),
(82,79,0),
(83,80,0),
(83,82,0),
(84,16,0),
(85,75,0),
(85,84,0),
(86,16,0);
/*!40000 ALTER TABLE `precedence` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `short_name` varchar(16) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES
(0,'Chief Engineer','CE'),
(1,'Researcher','RE'),
(2,'Operator','OP'),
(3,'Scientist','SC');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subsystem`
--

DROP TABLE IF EXISTS `subsystem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subsystem` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `long_name` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subsystem`
--

LOCK TABLES `subsystem` WRITE;
/*!40000 ALTER TABLE `subsystem` DISABLE KEYS */;
INSERT INTO `subsystem` VALUES
(0,'Master','MASTER CHECKLIST FOR GLOBAL INITIAL/FINAL PROCEDURES'),
(1,'Combustion Driver','COMBUSTION CHAMBER FILLING AND FIRING'),
(2,'Vacuum','VACUUM PROCEDURE'),
(3,'Test Gases (CT, ST)','TEST GAS (CT, ST) FILLING PROCEDURE'),
(4,'Shock Detection System','SHOCK DETECTION SYSTEM PROCEDURE'),
(5,'Optical Diagnostics','OPTICAL DIAGNOSTICS PROCEDURE'),
(6,'Microwave Diagnostics','MICROWAVE DIAGNOSTICS PROCEDURE');
/*!40000 ALTER TABLE `subsystem` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-07-09 13:00:29
