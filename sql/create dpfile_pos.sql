SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[dpfile_pos](
	[store_nbr] [int] NOT NULL,
	[pos_nbr] [varchar](10) NOT NULL,
	[ip_nbr] [varchar](255) NULL,
	[modification_date] [datetime] NULL,
	[size_bytes] [int] NULL
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
ALTER TABLE [dbo].[dpfile_pos] ADD  CONSTRAINT [PK_dpfile_posPT] PRIMARY KEY CLUSTERED 
(
	[store_nbr] ASC,
	[pos_nbr] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
