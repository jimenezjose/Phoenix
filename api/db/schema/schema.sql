/* NOTE to allow 0 timestamp: use the following */
/*SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';*/
/*SET SQL_MODE='ALLOW_INVALID_DATES';*/
/* url: https://stackoverflow.com/questions/9192027/invalid-default-value-for-create-date-timestamp-field */

CREATE TABLE `hostnames` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`hostname` varchar(255) NOT NULL,
	`retired` ENUM('true', 'false') NOT NULL DEFAULT 'false',
	PRIMARY KEY (`id`)
);

CREATE TABLE `attributes` (
	`attribute` varchar(255) NOT NULL,
	PRIMARY KEY (`attribute`)
);

CREATE TABLE `groups` (
	`group` varchar(255) NOT NULL,
	PRIMARY KEY (`group`)
);

CREATE TABLE `facts` (
	`fact` varchar(255) NOT NULL,
	PRIMARY KEY (`fact`)
);

CREATE TABLE `hostnames_attributes` (
	`id` INT(255) NOT NULL AUTO_INCREMENT,
	`ha_hostnames_id` INT NOT NULL,
	`ha_attribute` varchar(255) NOT NULL,
	`ha_value` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `hostnames_groups` (
	`id` INT(255) NOT NULL,
	`hg_hostnames_id` INT NOT NULL,
	`hg_group` varchar(255) NOT NULL,
	`hg_value` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `hostnames_facts` (
	`id` INT(255) NOT NULL,
	`hf_hostnames_id` INT NOT NULL,
	`hf_fact` varchar(255) NOT NULL,
	`hf_value` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `hostnames_groups_attributes` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`hostnames_groups_id` INT NOT NULL,
	`hga_attribute` varchar(255) NOT NULL,
	`hga_value` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `hostnames_facts_attributes` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`hostnames_facts_id` INT NOT NULL,
	`hfa_attribute` varchar(255) NOT NULL,
	`hfa_value` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `tests` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` varchar(255) NOT NULL UNIQUE,
	`steps` varchar(255) DEFAULT NULL,
	PRIMARY KEY (`id`)
);

/* added table to queue tests on currently running tests_runs on a busy server */
CREATE TABLE `tests_runs_queue` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `tests_runs_id` INT NOT NULL,
        PRIMARY KEY (`id`)
);

CREATE TABLE `tests_runs` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`hostnames_id` INT NOT NULL,
	`tests_id` INT NOT NULL,
	`start_timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`end_timestamp` TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
	`statuses_id` INT NOT NULL,
	`notes` TEXT,
	`config` TEXT,
	`scratch` TEXT,
	PRIMARY KEY (`id`)
);

CREATE TABLE `statuses` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` varchar(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE `test_logs` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`tests_runs_id` INT NOT NULL,
	`files_id` blob NOT NULL,
	`timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`)
);

CREATE TABLE `commands_queue` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`tests_runs_id` INT NOT NULL,
	`commands_id` INT NOT NULL,
	`completed` ENUM('true', 'false') NOT NULL DEFAULT 'false',
	PRIMARY KEY (`id`)
);

CREATE TABLE `commands` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` varchar(255) NOT NULL UNIQUE,
	`command` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `tests_commands` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`tests_id` INT NOT NULL,
	`commands_id` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `files` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` varchar(255) NOT NULL,
	`location` TEXT NOT NULL,
	PRIMARY KEY (`id`)
);

ALTER TABLE `hostnames_attributes` ADD CONSTRAINT `hostnames_attributes_fk0` FOREIGN KEY (`ha_hostnames_id`) REFERENCES `hostnames`(`id`);

ALTER TABLE `hostnames_attributes` ADD CONSTRAINT `hostnames_attributes_fk1` FOREIGN KEY (`ha_attribute`) REFERENCES `attributes`(`attribute`);

ALTER TABLE `hostnames_groups` ADD CONSTRAINT `hostnames_groups_fk0` FOREIGN KEY (`hg_hostnames_id`) REFERENCES `hostnames`(`id`);

ALTER TABLE `hostnames_groups` ADD CONSTRAINT `hostnames_groups_fk1` FOREIGN KEY (`hg_group`) REFERENCES `groups`(`group`);

ALTER TABLE `hostnames_facts` ADD CONSTRAINT `hostnames_facts_fk0` FOREIGN KEY (`hf_hostnames_id`) REFERENCES `hostnames`(`id`);

ALTER TABLE `hostnames_facts` ADD CONSTRAINT `hostnames_facts_fk1` FOREIGN KEY (`hf_fact`) REFERENCES `facts`(`fact`);

ALTER TABLE `hostnames_groups_attributes` ADD CONSTRAINT `hostnames_groups_attributes_fk0` FOREIGN KEY (`hostnames_groups_id`) REFERENCES `hostnames_groups`(`id`);

ALTER TABLE `hostnames_groups_attributes` ADD CONSTRAINT `hostnames_groups_attributes_fk1` FOREIGN KEY (`hga_attribute`) REFERENCES `attributes`(`attribute`);

ALTER TABLE `hostnames_facts_attributes` ADD CONSTRAINT `hostnames_facts_attributes_fk0` FOREIGN KEY (`hostnames_facts_id`) REFERENCES `hostnames_facts`(`id`);

ALTER TABLE `hostnames_facts_attributes` ADD CONSTRAINT `hostnames_facts_attributes_fk1` FOREIGN KEY (`hfa_attribute`) REFERENCES `attributes`(`attribute`);

ALTER TABLE `tests_runs` ADD CONSTRAINT `tests_runs_fk0` FOREIGN KEY (`hostnames_id`) REFERENCES `hostnames`(`id`);

ALTER TABLE `tests_runs` ADD CONSTRAINT `tests_runs_fk1` FOREIGN KEY (`tests_id`) REFERENCES `tests`(`id`);

ALTER TABLE `tests_runs` ADD CONSTRAINT `tests_runs_fk2` FOREIGN KEY (`status`) REFERENCES `statuses`(`id`);

ALTER TABLE `test_logs` ADD CONSTRAINT `test_logs_fk0` FOREIGN KEY (`tests_runs_id`) REFERENCES `tests_runs`(`id`);

ALTER TABLE `test_logs` ADD CONSTRAINT `test_logs_fk1` FOREIGN KEY (`files_id`) REFERENCES `files`(`id`);

ALTER TABLE `commands_queue` ADD CONSTRAINT `commands_queue_fk0` FOREIGN KEY (`tests_runs_id`) REFERENCES `tests_runs`(`id`);

ALTER TABLE `commands_queue` ADD CONSTRAINT `commands_queue_fk1` FOREIGN KEY (`commands_id`) REFERENCES `commands`(`id`);

ALTER TABLE `tests_commands` ADD CONSTRAINT `tests_commands_fk0` FOREIGN KEY (`tests_id`) REFERENCES `tests`(`id`);

ALTER TABLE `tests_commands` ADD CONSTRAINT `tests_commands_fk1` FOREIGN KEY (`commands_id`) REFERENCES `commands`(`id`);

