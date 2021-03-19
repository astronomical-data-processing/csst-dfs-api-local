/*==============================================================*/
/* Table: ifs_result_0_1                                         */
/*==============================================================*/
create table ifs_result_0_1 (
   result0_id            INT                 not null,
   result1_id            INT                 not null,
   create_time          DATETIME                 null,
   primary key (result0_id, result1_id)
);

/*==============================================================*/
/* Table: ifs_raw_ref                                           */
/*==============================================================*/
create table ifs_raw_ref (
   fit_id               INT                 not null,
   ref_id               INT                 not null,
   create_time          DATETIME                 null,
   primary key (fit_id, ref_id)
);

/*==============================================================*/
/* Table: ifs_rawfits                                           */
/*==============================================================*/
create table ifs_rawfits (
   id             integer PRIMARY KEY autoincrement,
   filename             VARCHAR(100)         null,
   obs_time             INT             null,
   ccd_num              INT                  null,
   exp_time             DATETIME             null,
   file_path            VARCHAR(128)         null,
   qc0_status           tinyint(1)           null,
   qc0_time             DATETIME                 null,
   prc_status           tinyint(1)           null,
   prc_time             DATETIME                 null,
   create_time          DATETIME                 null
);

/*==============================================================*/
/* Table: ifs_ref_fits                                          */
/*==============================================================*/
create table ifs_ref_fits (
   id             integer PRIMARY KEY autoincrement,
   filename             VARCHAR(128)         null,
   obs_time             INT             null,
   exp_time             DATETIME             null,
   ccd_num              INT                  null,
   file_path            VARCHAR(256)         null,
   ref_type             VARCHAR(32)          null,
   create_time          DATETIME             null,
   status               tinyint(1)           null
);

/*==============================================================*/
/* Table: ifs_result_0                                          */
/*==============================================================*/
create table ifs_result_0 (
   id             integer PRIMARY KEY autoincrement,
   filename             VARCHAR(100)         null,
   raw_id               INT                  null,
   file_path            VARCHAR(128)         null,
   create_time          DATETIME             null,
   proc_type            VARCHAR(32)          null
);

/*==============================================================*/
/* Table: ifs_result_1                                          */
/*==============================================================*/
create table ifs_result_1 (
   id             integer PRIMARY KEY autoincrement,
   filename             VARCHAR(100)         null,
   file_path            VARCHAR(128)         null,
   create_time          DATETIME             null,
   proc_type            VARCHAR(32)          null
);
