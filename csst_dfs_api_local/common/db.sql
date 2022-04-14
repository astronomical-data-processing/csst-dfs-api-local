/*----------------facility------------------------------*/
drop table if exists t_module_status;

drop table if exists t_observation;

drop table if exists t_detector;

drop table if exists t_detector_status;

drop table if exists t_facility_status;

drop table if exists t_guiding;

/*----------------msc------------------------------*/
drop table if exists msc_level0_data;

drop table if exists msc_level0_header;

drop table if exists msc_level0_prc;

drop table if exists msc_cal2level0;

drop table if exists msc_cal_header;

drop table if exists msc_cal_merge;

drop table if exists msc_level1_data;

drop table if exists msc_level1_header;

drop table if exists msc_level1_prc;

drop table if exists msc_level1_ref;
/*----------------ifs------------------------------*/

drop table if exists ifs_level0_data;

drop table if exists ifs_level0_header;

drop table if exists ifs_level0_prc;

drop table if exists ifs_cal2level0;

drop table if exists ifs_cal_header;

drop table if exists ifs_cal_merge;

drop table if exists ifs_level1_data;

drop table if exists ifs_level1_header;

drop table if exists ifs_level1_prc;

drop table if exists ifs_level1_ref;

/*----------------sls------------------------------*/
drop table if exists sls_level0_data;

drop table if exists sls_level0_header;

drop table if exists sls_level0_prc;

drop table if exists sls_cal2level0;

drop table if exists sls_cal_header;

drop table if exists sls_cal_merge;

drop table if exists sls_level1_data;

drop table if exists sls_level1_header;

drop table if exists sls_level1_prc;

drop table if exists sls_level1_ref;

drop table if exists sls_level2_spectra;

/*===========================facility===================================*/
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

/*===========================msc===================================*/
create table msc_level0_data
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

create table msc_level0_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

create table msc_level0_prc
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
create table msc_level1_data
(
   id                   integer PRIMARY KEY autoincrement,
   level0_id            varchar(20) not null,
   data_type            varchar(64) not null,
   cor_sci_id           int(20),
   prc_params           varchar(1024),
   filename             varchar(128),
   file_path            varchar(256),
   prc_status           tinyint(1),
   prc_time             datetime,
   qc1_status           tinyint(1),
   qc1_time             datetime,
   create_time          datetime,
   pipeline_id          varchar(60)
);
create table msc_level1_ref (
  level1_id int(20) not null,
  ref_type varchar(64) not null,
  cal_id int(20) not null,
  primary key (level1_id, ref_type)
);
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
create table msc_cal2level0
(
   merge_id             int(20) not null,
   level0_id            varchar(20) not null,
   primary key (merge_id, level0_id)
);

create table msc_cal_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

create table msc_cal_merge
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
create table msc_level1_prc
(
   id                   integer PRIMARY KEY autoincrement,
   level1_id            int(20) not null,
   pipeline_id          varchar(64) not null,
   prc_module           varchar(32) not null,
   params_file_path     varchar(256),
   prc_status           int(2),
   prc_time             datetime,
   result_file_path            varchar(256)
);
/*===========================ifs===================================*/
create table ifs_level0_data
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

create table ifs_level0_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

create table ifs_level0_prc
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
create table ifs_cal2level0
(
   merge_id             int(20) not null,
   level0_id            varchar(20) not null,
   primary key (merge_id, level0_id)
);

create table ifs_cal_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

create table ifs_cal_merge
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

create table ifs_level1_data
(
   id                   integer PRIMARY KEY autoincrement,
   level0_id            varchar(20) not null,
   data_type            varchar(64) not null,
   cor_sci_id           int(20),
   prc_params           varchar(1024),
   filename             varchar(128),
   file_path            varchar(256),
   prc_status           tinyint(1),
   prc_time             datetime,
   qc1_status           tinyint(1),
   qc1_time             datetime,
   create_time          datetime,
   pipeline_id          varchar(60)
);

create table ifs_level1_ref (
  level1_id int(20) not null,
  ref_type varchar(64) not null,
  cal_id int(20) not null,
  primary key (level1_id, ref_type)
);

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
create table ifs_level1_prc
(
   id                   integer PRIMARY KEY autoincrement,
   level1_id            int(20) not null,
   pipeline_id          varchar(64) not null,
   prc_module           varchar(32) not null,
   params_file_path     varchar(256),
   prc_status           int(2),
   prc_time             datetime,
   result_file_path            varchar(256)
);
/*===========================sls===================================*/
create table sls_level0_data
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

create table sls_level0_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

create table sls_level0_prc
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
create table sls_cal2level0
(
   merge_id             int(20) not null,
   level0_id            varchar(20) not null,
   primary key (merge_id, level0_id)
);

create table sls_cal_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

create table sls_cal_merge
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

create table sls_level1_data
(
   id                   integer PRIMARY KEY autoincrement,
   level0_id            varchar(20) not null,
   data_type            varchar(64) not null,
   prc_params           varchar(1024),
   filename             varchar(128),
   file_path            varchar(256),
   prc_status           tinyint(1),
   prc_time             datetime,
   qc1_status           tinyint(1),
   qc1_time             datetime,
   create_time          datetime,
   pipeline_id          varchar(60)
);

create table sls_level1_ref (
  level1_id int(20) not null,
  ref_type varchar(64) not null,
  cal_id int(20) not null,
  primary key (level1_id, ref_type)
);

create table sls_level1_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);

create table sls_level1_prc
(
   id                   integer PRIMARY KEY autoincrement,
   level1_id            int(20) not null,
   pipeline_id          varchar(64) not null,
   prc_module           varchar(32) not null,
   params_file_path     varchar(256),
   prc_status           int(2),
   prc_time             datetime,
   result_file_path     varchar(256)
);

create table sls_level2_spectra
(
   id                   integer PRIMARY KEY autoincrement,
   spectra_id           varchar(40),
   level1_id            int(20) not null,
   region               varchar(128),
   filename             varchar(128),
   file_path            varchar(256),
   prc_status           tinyint(1),
   prc_time             datetime,
   qc1_status           tinyint(1),
   qc1_time             datetime,
   create_time          datetime,
   pipeline_id          varchar(60)
);
create table sls_level2_spectra_header
(
   id                   int(20) not null,
   obs_time             datetime,
   exp_time             float,
   ra                   float,
   "dec"                float,
   create_time          datetime,
   primary key (id)
);
-- csst.msc_level2_catalog definition

CREATE TABLE msc_level2_catalog (
  source_id integer PRIMARY KEY autoincrement,
  obs_id varchar(12),
  detector_no char(2),
  seq int(20),
  flux_aper_1 double,
  flux_aper_2 double,
  flux_aper_3 double,
  flux_aper_4 double,
  flux_aper_5 double,
  flux_aper_6 double,
  flux_aper_7 double,
  flux_aper_8 double,
  flux_aper_9 double,
  flux_aper_10 double,
  flux_aper_11 double,
  flux_aper_12 double,
  fluxerr_aper_1 double,
  fluxerr_aper_2 double,
  fluxerr_aper_3 double,
  fluxerr_aper_4 double,
  fluxerr_aper_5 double,
  fluxerr_aper_6 double,
  fluxerr_aper_7 double,
  fluxerr_aper_8 double,
  fluxerr_aper_9 double,
  fluxerr_aper_10 double,
  fluxerr_aper_11 double,
  fluxerr_aper_12 double,
  mag_aper_1 double,
  mag_aper_2 double,
  mag_aper_3 double,
  mag_aper_4 double,
  mag_aper_5 double,
  mag_aper_6 double,
  mag_aper_7 double,
  mag_aper_8 double,
  mag_aper_9 double,
  mag_aper_10 double,
  mag_aper_11 double,
  mag_aper_12 double,
  magerr_aper_1 double,
  magerr_aper_2 double,
  magerr_aper_3 double,
  magerr_aper_4 double,
  magerr_aper_5 double,
  magerr_aper_6 double,
  magerr_aper_7 double,
  magerr_aper_8 double,
  magerr_aper_9 double,
  magerr_aper_10 double,
  magerr_aper_11 double,
  magerr_aper_12 double,
  flux_auto double,
  fluxerr_auto double,
  mag_auto double,
  magerr_auto double,
  kron_radius double,
  background double,
  x_image double,
  y_image double,
  alpha_j2000 double,
  delta_j2000 double,
  a_image double,
  b_image double,
  theta_image double,
  a_world double,
  b_world double,
  theta_world double,
  theta_j2000 double,
  errx2_image double,
  erry2_image double,
  erra_image double,
  errb_image double,
  errtheta_image double,
  erra_world double,
  errb_world double,
  errtheta_world double,
  errtheta_j2000 double,
  xwin_image double,
  ywin_image double,
  alphawin_j2000 double,
  deltawin_j2000 double,
  errx2win_image double,
  erry2win_image double,
  flags int(20),
  flags_weight int(20),
  imaflags_iso double,
  nimaflags_iso double,
  fwhm_image double,
  fwhm_world double,
  elongation double,
  ellipticity double,
  class_star double,
  flux_radius double,
  fwhmpsf_image double,
  fwhmpsf_world double,
  xpsf_image double,
  ypsf_image double,
  alphapsf_j2000 double,
  deltapsf_j2000 double,
  flux_psf double,
  fluxerr_psf double,
  mag_psf double,
  magerr_psf double,
  niter_psf int(20),
  chi2_psf double,
  errx2psf_image double,
  erry2psf_image double,
  chi2_model double,
  flags_model tinyint(1),
  niter_model int(20),
  flux_model double,
  fluxerr_model double,
  mag_model double,
  magerr_model double,
  flux_hybrid double,
  fluxerr_hybrid double,
  mag_hybrid double,
  magerr_hybrid double,
  flux_max_model double,
  mu_max_model double,
  flux_eff_model double,
  mu_eff_model double,
  flux_mean_model double,
  mu_mean_model double,
  xmodel_image double,
  ymodel_image double,
  alphamodel_j2000 double,
  deltamodel_j2000 double,
  erry2model_image double,
  erramodel_image double,
  errbmodel_image double,
  errthetamodel_image double,
  erramodel_world double,
  errbmodel_world double,
  errthetamodel_world double,
  errthetamodel_j2000 double,
  amodel_image double,
  bmodel_image double,
  thetamodel_image double,
  amodel_world double,
  bmodel_world double,
  thetamodel_world double,
  thetamodel_j2000 double,
  spread_model double,
  spreaderr_model double,
  noisearea_model double,
  flux_spheroid double,
  fluxerr_spheroid double,
  mag_spheroid double,
  magerr_spheroid double,
  flux_max_spheroid double,
  mu_max_spheroid double,
  flux_eff_spheroid double,
  mu_eff_spheroid double,
  flux_mean_spheroid double,
  mu_mean_spheroid double,
  fluxratio_spheroid double,
  fluxratioerr_spheroid double,
  spheroid_reff_image double,
  spheroid_refferr_image double,
  spheroid_reff_world double,
  spheroid_refferr_world double,
  spheroid_aspect_image double,
  spheroid_aspecterr_image double,
  spheroid_aspect_world double,
  spheroid_aspecterr_world double,
  spheroid_theta_image double,
  spheroid_thetaerr_image double,
  spheroid_theta_world double,
  spheroid_thetaerr_world double,
  spheroid_theta_j2000 double,
  spheroid_sersicn double,
  spheroid_sersicnerr double,
  flux_disk double,
  fluxerr_disk double,
  mag_disk double,
  magerr_disk double,
  flux_max_disk double,
  mu_max_disk double,
  flux_eff_disk double,
  mu_eff_disk double,
  flux_mean_disk double,
  mu_mean_disk double,
  fluxratio_disk double,
  fluxratioerr_disk double,
  disk_scale_image double,
  disk_scaleerr_image double,
  disk_scale_world double,
  disk_scaleerr_world double,
  disk_aspect_image double,
  disk_aspecterr_image double,
  disk_aspect_world double,
  disk_aspecterr_world double,
  disk_inclination double,
  disk_inclinationerr double,
  disk_theta_image double,
  disk_thetaerr_image double,
  disk_theta_world double,
  disk_thetaerr_world double,
  disk_theta_j2000 double,
  obs_time datetime
) ;