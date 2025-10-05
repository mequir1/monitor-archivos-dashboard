SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[vw_store_promos_update] as
select dpc.store_nbr, dpc.modification_date as central_modification_date, 
MAX(pos.modification_date) as store_modification_date,
case when MAX(pos.modification_date) >= dpc.modification_date  then 'True' else 'False' end status
from pmt_dpc dpc left join dpfile_pos pos on dpc.store_nbr=pos.store_nbr
GROUP BY dpc.store_nbr, dpc.modification_date;
GO
