/*
 Navicat Premium Dump SQL

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 80031 (8.0.31)
 Source Host           : localhost:3306
 Source Schema         : crewai_financial

 Target Server Type    : MySQL
 Target Server Version : 80031 (8.0.31)
 File Encoding         : 65001

 Date: 18/04/2025 21:24:55
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `age` int NOT NULL,
  `account_balance` decimal(10,2) NOT NULL,
  `deposit_amount` decimal(10,2) NOT NULL,
  `withdrawal_amount` decimal(10,2) NOT NULL,
  `investment_risk_tolerance` enum('low','moderate','high') COLLATE utf8mb4_unicode_ci NOT NULL,
  `investment_horizon` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `monthly_income` decimal(10,2) NOT NULL,
  `monthly_expenses` decimal(10,2) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=79 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
