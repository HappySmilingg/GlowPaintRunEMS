-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: gprems
-- ------------------------------------------------------
-- Server version	9.1.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event` (
  `eventID` int NOT NULL AUTO_INCREMENT,
  `eventName` varchar(100) NOT NULL,
  `eventDate` datetime NOT NULL,
  `eventLocation` varchar(255) NOT NULL,
  `eventPicture` varchar(255) DEFAULT NULL,
  `eventCapacity` int DEFAULT NULL,
  `modifiedDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`eventID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event`
--

LOCK TABLES `event` WRITE;
/*!40000 ALTER TABLE `event` DISABLE KEYS */;
/*!40000 ALTER TABLE `event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eventdetails`
--

DROP TABLE IF EXISTS `eventdetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eventdetails` (
  `eventDetailID` int NOT NULL AUTO_INCREMENT,
  `eventID` int DEFAULT NULL,
  `detailName` varchar(100) DEFAULT NULL,
  `detailPicture` varchar(255) DEFAULT NULL,
  `detailDescription` json DEFAULT NULL,
  `modifiedDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`eventDetailID`),
  KEY `eventID` (`eventID`),
  CONSTRAINT `eventdetails_ibfk_1` FOREIGN KEY (`eventID`) REFERENCES `event` (`eventID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eventdetails`
--

LOCK TABLES `eventdetails` WRITE;
/*!40000 ALTER TABLE `eventdetails` DISABLE KEYS */;
/*!40000 ALTER TABLE `eventdetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory` (
  `inventoryID` int NOT NULL AUTO_INCREMENT,
  `itemID` int DEFAULT NULL,
  `stockQuantity` int NOT NULL DEFAULT '0',
  `stockStatus` enum('available','unavailable') NOT NULL DEFAULT 'available',
  `modifiedDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`inventoryID`),
  KEY `itemID` (`itemID`),
  CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`itemID`) REFERENCES `items` (`itemID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory`
--

LOCK TABLES `inventory` WRITE;
/*!40000 ALTER TABLE `inventory` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `itemID` int NOT NULL AUTO_INCREMENT,
  `itemName` varchar(100) NOT NULL,
  `itemType` varchar(50) NOT NULL,
  `itemPrice` decimal(10,2) NOT NULL,
  `itemDescription` json DEFAULT NULL,
  `itemStatus` enum('active','inactive') DEFAULT 'active',
  `modifiedDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`itemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `orderID` int NOT NULL AUTO_INCREMENT,
  `itemID` int DEFAULT NULL,
  `orderDate` datetime DEFAULT CURRENT_TIMESTAMP,
  `totalAmount` decimal(10,2) NOT NULL,
  `orderStatus` enum('paid','unpaid') NOT NULL DEFAULT 'unpaid',
  `userID` int DEFAULT NULL,
  `modifiedDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`orderID`),
  KEY `itemID` (`itemID`),
  KEY `userID` (`userID`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`itemID`) REFERENCES `items` (`itemID`) ON DELETE SET NULL,
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `paymentID` int NOT NULL AUTO_INCREMENT,
  `orderID` int DEFAULT NULL,
  `paymentDate` datetime DEFAULT NULL,
  `invoiceNo` varchar(50) DEFAULT NULL,
  `paymentType` varchar(50) DEFAULT NULL,
  `paymentStatus` enum('pending','completed') DEFAULT 'pending',
  `modifiedDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`paymentID`),
  KEY `orderID` (`orderID`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`orderID`) REFERENCES `orders` (`orderID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `userID` int NOT NULL AUTO_INCREMENT,
  `userName` varchar(100) NOT NULL,
  `userEmail` varchar(100) NOT NULL,
  `userPhone` varchar(15) NOT NULL,
  `userDescription` json DEFAULT NULL,
  `userPassword` varchar(255) DEFAULT NULL,
  `userType` enum('admin','student','public') NOT NULL,
  `userStatus` enum('active','registered','check-in1','check-in2','check-in3','deleted') NOT NULL DEFAULT 'active',
  `registeredDate` datetime DEFAULT NULL,
  `checkInTime` datetime DEFAULT NULL,
  `modifiedDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`userID`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','123@gmail.com','012-3456789',NULL,'123','admin','active','2024-11-16 12:27:18',NULL,'2024-11-16 04:27:18'),(2,'Kenny Ooi Yun Shuen','kenny@student.usm.my','016-4153366','{\"campus\": \"main\", \"school\": \"computer-science\", \"package\": \"Lite\", \"tShirtSize\": \"XL\", \"matricNumber\": \"157866\"}',NULL,'student','registered','2024-11-16 17:29:32',NULL,'2024-11-16 09:32:30'),(3,'John Doe','john@gmail.com','016-4155555','{\"package\": \"Pro\", \"ICNumber\": \"020810020388\", \"tShirtSize\": \"3XL\"}',NULL,'public','registered','2024-11-16 17:30:58',NULL,'2024-11-16 09:32:50'),(4,'Tan Tien Ping','tienpingtan@student.usm.my','016-2348888','{\"campus\": \"engineering\", \"school\": \"ee\", \"package\": \"Pro\", \"tShirtSize\": \"M\", \"matricNumber\": \"159235\"}',NULL,'student','registered','2024-11-16 18:05:51',NULL,'2024-11-16 10:05:50'),(5,'Muhammad Bin Alif','alif98@gmail.com','016-9253323','{\"package\": \"Pro\", \"ICNumber\": \"980308060723\", \"tShirtSize\": \"3XL\"}',NULL,'public','registered','2024-11-16 18:07:12',NULL,'2024-11-16 10:17:01'),(6,'Khoo Jia Jin','jiajin@student.usm.my','012-4325423','{\"campus\": \"main\", \"school\": \"pharm\", \"package\": \"Lite\", \"tShirtSize\": \"S\", \"matricNumber\": \"158876\"}',NULL,'student','registered','2024-11-16 18:08:21',NULL,'2024-11-16 10:08:20'),(7,'Ahmad bin Ismail','ismail02@student.usm.my','012-3324352','{\"campus\": \"health\", \"school\": \"health\", \"package\": \"Starter\", \"tShirtSize\": \"S\", \"matricNumber\": \"157562\"}',NULL,'student','registered','2024-11-16 18:11:53',NULL,'2024-11-16 10:11:52'),(8,'Muhammad Binti Siti','siti@gmail.com','016-4154225','{\"package\": \"Pro\", \"ICNumber\": \"990606062932\", \"tShirtSize\": \"M\"}',NULL,'public','registered','2024-11-16 18:18:12',NULL,'2024-11-16 10:18:12'),(9,'Jonathan Yap Jia Sheng','jonathan@gmail.com','012-3065006','{\"package\": \"Pro\", \"ICNumber\": \"020920072933\", \"tShirtSize\": \"L\"}',NULL,'public','registered','2024-11-16 18:20:19',NULL,'2024-11-16 10:20:19');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'gprems'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-16 18:28:56
