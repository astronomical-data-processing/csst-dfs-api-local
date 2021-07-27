drop table if exists ifs_level1_data;

drop table if exists ifs_level1_header;

drop table if exists msc_level1_data;

drop table if exists msc_level1_header;

drop table if exists t_cal2level0;

drop table if exists t_cal_header;

drop table if exists t_cal_merge;

drop table if exists t_detector;

drop table if exists t_detector_status;

drop table if exists t_facility_status;

drop table if exists t_guiding;

drop table if exists t_level0_data;

drop table if exists t_level0_header;

drop table if exists t_level0_prc;

drop table if exists t_module_status;

drop table if exists t_observation;

/*==============================================================*/
/* Table: ifs_level1_data                                       */
/*==============================================================*/
create table ifs_level1_data
(
   id                   integer PRIMARY KEY autoincrement,
   level0_id            varchar(20) not null,
   data_type            varchar(64) not null,
   cor_sci_id           int(20),
   prc_params           varchar(1024),
   flat_id              int(20),
   dark_id              int(20),
   bias_id              int(20),
   lamp_id              int(20),
   arc_id               int(20),
   sky_id               int(20),
   filename             varchar(128),
   file_path            varchar(256),
   prc_status           tinyint(1),
   prc_time             datetime,
   qc1_status           tinyint(1),
   qc1_time             datetime,
   create_time          datetime,
   pipeline_id          varchar(60)
);

/*==============================================================*/
/* Table: ifs_level1_header                                     */
/*==============================================================*/
create table ifs_level1_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

/*==============================================================*/
/* Table: msc_level1_data                                       */
/*==============================================================*/
create table msc_level1_data
(
   id                   integer PRIMARY KEY autoincrement,
   level0_id            varchar(20) not null,
   data_type            varchar(64) not null,
   cor_sci_id           int(20),
   prc_params           varchar(1024),
   flat_id              int(20),
   dark_id              int(20),
   bias_id              int(20),
   filename             varchar(128),
   file_path            varchar(256),
   prc_status           tinyint(1),
   prc_time             datetime,
   qc1_status           tinyint(1),
   qc1_time             datetime,
   create_time          datetime,
   pipeline_id          varchar(60)
);

/*==============================================================*/
/* Table: msc_level1_header                                     */
/*==============================================================*/
create table msc_level1_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

/*==============================================================*/
/* Table: t_cal2level0                                          */
/*==============================================================*/
create table t_cal2level0
(
   merge_id             int(20) not null,
   level0_id            varchar(20) not null,
   primary key (merge_id, level0_id)
);

/*==============================================================*/
/* Table: t_cal_header                                          */
/*==============================================================*/
create table t_cal_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

/*==============================================================*/
/* Table: t_cal_merge                                           */
/*==============================================================*/
create table t_cal_merge
(
   id                   integer PRIMARY KEY autoincrement,
   cal_id               varchar(20) not null,
   detector_no          varchar(10) not null,
   ref_type             varchar(16),
   obs_time             datetime,
   exp_time             float,
   filename             varchar(128),
   file_path            varchar(256),
   qc1_status           tinyint(1),
   qc1_time             datetime,
   prc_status           tinyint(1),
   prc_time             datetime,
   create_time          datetime
);

/*==============================================================*/
/* Table: t_detector                                            */
/*==============================================================*/
create table t_detector
(
   no                   varchar(10) not null,
   detector_name        varchar(256) not null,
   module_id            varchar(20),
   filter_id            varchar(20),
   create_time          datetime,
   update_time          datetime,
   primary key (no)
);

/*==============================================================*/
/* Table: t_detector_status                                     */
/*==============================================================*/
create table t_detector_status
(
   id                   integer PRIMARY KEY autoincrement,
   detector_no          varchar(10) not null,
   status               varchar(256) not null,
   status_time          datetime,
   create_time          datetime
);

/*==============================================================*/
/* Table: t_facility_status                                     */
/*==============================================================*/
create table t_facility_status
(
   id                   integer PRIMARY KEY autoincrement,
   status               varchar(256) not null,
   status_time          datetime,
   create_time          datetime
);

/*==============================================================*/
/* Table: t_guiding                                             */
/*==============================================================*/
create table t_guiding
(
   id                   integer PRIMARY KEY autoincrement,
   filename             varbinary(128),
   guiding_file_path    varchar(256) not null,
   guiding_no           varchar(256),
   create_time          datetime
);

/*==============================================================*/
/* Table: t_level0_data                                         */
/*==============================================================*/
create table t_level0_data
(
   id                   integer PRIMARY KEY autoincrement,
   level0_id            varchar(20) not null,
   obs_id               varchar(10) not null,
   detector_no          varchar(10) not null,
   obs_type             varchar(16),
   obs_time             datetime,
   exp_time             float,
   detector_status_id   int(20),
   filename             varchar(128),
   file_path            varchar(256),
   qc0_status           tinyint(1),
   qc0_time             datetime,
   prc_status           tinyint(1),
   prc_time             datetime,
   create_time          datetime
);

/*==============================================================*/
/* Table: t_level0_header                                       */
/*==============================================================*/
create table t_level0_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

/*==============================================================*/
/* Table: t_level0_prc                                          */
/*==============================================================*/
create table t_level0_prc
(
   id                   integer PRIMARY KEY autoincrement,
   level0_id            varchar(20) not null,
   pipeline_id          varchar(64) not null,
   prc_module           varchar(32) not null,
   params_file_path     varchar(256),
   prc_status           int(2),
   prc_time             datetime,
   result_file_path            varchar(256)
);

/*==============================================================*/
/* Table: t_module_status                                       */
/*==============================================================*/
create table t_module_status
(
   id                   integer PRIMARY KEY autoincrement,
   module_id            varbinary(20),
   status               varchar(256) not null,
   status_time          datetime,
   create_time          datetime
);

/*==============================================================*/
/* Table: t_observation                                         */
/*==============================================================*/
create table t_observation
(
   id                   integer PRIMARY KEY autoincrement,
   obs_id               varchar(10),
   obs_time             datetime,
   exp_time             float,
   module_id            varchar(20),
   obs_type             varchar(16),
   facility_status_id   int(20),
   module_status_id     int(20),
   qc0_status           tinyint(1),
   qc0_time             datetime,
   prc_status           tinyint(1),
   prc_time             datetime,
   create_time          datetime,
   import_status        tinyint(1)
);

