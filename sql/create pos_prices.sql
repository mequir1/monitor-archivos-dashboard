SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[pos_prices](
	[store_nbr] [int] NOT NULL,
	[item_nbr] [varchar](10) NOT NULL,
	[upc_code] [varchar](14) NOT NULL,
	[upc_description] [varchar](255) NULL,
	[previous_base_price] [decimal](18, 2) NULL,
	[new_base_price] [decimal](18, 2) NULL,
	[previous_customer_price] [decimal](18, 2) NULL,
	[new_customer_price] [decimal](18, 2) NULL,
	[modification_date] [datetime] NULL
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
ALTER TABLE [dbo].[pos_prices] ADD  CONSTRAINT [PK_pos_pricesPT] PRIMARY KEY CLUSTERED 
(
	[store_nbr] ASC,
	[item_nbr] ASC,
	[upc_code] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
