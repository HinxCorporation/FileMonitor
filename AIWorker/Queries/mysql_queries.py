# Mysql_Queries.py

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS file_info (
    file_name VARCHAR(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    file_path VARCHAR(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    creation_date DATETIME,
    modification_date DATETIME,
    access_date DATETIME,
    file_permissions VARCHAR(64),
    owner VARCHAR(64),
    last_accessed_by VARCHAR(64),
    storage_id VARCHAR(128) NOT NULL,
    md5 CHAR(32),
    partition_id INT NOT NULL,
    PRIMARY KEY (storage_id,partition_id)
)
PARTITION BY LIST (partition_id) (
    PARTITION p_z VALUES IN (1)
);
"""

INSERT_DATA = """
INSERT INTO file_info (file_name, file_size, file_type, file_path, creation_date, 
                       modification_date, access_date, file_permissions, owner, 
                       last_accessed_by, storage_id, md5, partition_id) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

UPDATE_DATA = """
UPDATE file_info 
SET file_name = %s, file_size = %s, file_type = %s, file_path = %s, creation_date = %s, 
    modification_date = %s, access_date = %s, file_permissions = %s, owner = %s, 
    last_accessed_by = %s, md5 = %s
WHERE storage_id = %s AND partition_id = %s;
"""

DELETE_DATA = """
DELETE FROM file_info 
WHERE storage_id = %s AND partition_id = %s;
"""

SELECT_DATA = """
SELECT * FROM file_info 
WHERE storage_id = %s AND partition_id = %s;
"""

LIST_PARTITIONS = """
SELECT PARTITION_DESCRIPTION
FROM INFORMATION_SCHEMA.PARTITIONS 
WHERE TABLE_NAME = 'file_info';
"""

ADD_PARTITION = """ALTER TABLE file_info ADD PARTITION (PARTITION %s VALUES IN (%s));"""

# SQL to create a mapping table for top 3-level paths to partition IDs
CREATE_T3L_PARTITION_MAPPING = """
CREATE TABLE IF NOT EXISTS t3l_partition_mapping (
    t3l_path VARCHAR(255) PRIMARY KEY,
    partition_id INT
);
"""

# SQL to insert a new path-to-partition ID mapping
INSERT_PARTITION_MAPPING = """
INSERT INTO t3l_partition_mapping (t3l_path, partition_id) VALUES (%s, %s)
"""

# SQL to retrieve the partition ID for a given path
GET_PARTITION_ID = """
SELECT partition_id FROM t3l_partition_mapping WHERE t3l_path = %s
"""

# SQL to check if a specific partition exists in the file_info table
CHECK_PARTITION_EXISTS = """
SELECT COUNT(*) FROM information_schema.partitions 
WHERE table_schema = 'test_fm' AND table_name = 'file_info' AND partition_name = %s
"""

SELECT_PARTITION_MAPPING = """
SELECT * FROM t3l_partition_mapping
"""

# SQL to add a new partition to the file_info table
ADD_NEW_PARTITION = """
ALTER TABLE file_info ADD PARTITION (PARTITION p%s VALUES LESS THAN (%s))
"""

# Replace 'your_database_name' with the actual name of your database.

DEMO_CLEAR_ALL = """
drop table test_fm.file_info;
drop table test_fm.t3l_partition_mapping;
"""