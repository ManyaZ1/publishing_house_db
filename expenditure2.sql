WITH PartnerCosts AS (
    SELECT 
        strftime('%Y', "contributes"."payment_date") AS Year,
        SUM("CONTRACT"."payment") AS Total_Payment,
        0 AS Total_Printing_Cost
    FROM "CONTRACT"
    JOIN "contributes" 
        ON "CONTRACT"."Partner_Tax_Id" = "contributes"."Partner_TaxId"
        AND "CONTRACT"."Publication-isbn" = "contributes"."Publication-isbn"
    WHERE "contributes"."payment_date" IS NOT NULL
    GROUP BY Year
),
PrintingCosts AS (
    SELECT 
        strftime('%Y', "order_printing_house"."delivery date") AS Year,
        0 AS Total_Payment,
        SUM("order_printing_house"."cost") AS Total_Printing_Cost
    FROM "order_printing_house"
    WHERE "order_printing_house"."delivery date" IS NOT NULL
    GROUP BY Year
)
SELECT 
    Year,
    SUM(Total_Payment) AS Total_Payment,
    SUM(Total_Printing_Cost) AS Total_Printing_Cost,
    SUM(Total_Payment + Total_Printing_Cost) AS Combined_Cost
FROM (
    SELECT * FROM PartnerCosts
    UNION ALL
    SELECT * FROM PrintingCosts
)
GROUP BY Year
ORDER BY Year;
