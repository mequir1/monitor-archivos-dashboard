SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[vw_pos_promos_update] as
select dpc.store_nbr, dpc.modification_date as central_modification_date, pos.modification_date as store_modification_date,
pos.pos_nbr ,
case when dpc.modification_date >= pos.modification_date then 'True' else 'False' end status
from pmt_dpc dpc
left join dpfile_pos pos on dpc.store_nbr=pos.store_nbr
GO
