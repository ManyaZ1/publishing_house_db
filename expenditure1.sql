
SELECT 
    strftime('%Y', "contributes"."payment_date") AS Year, -- Extract the year from payment_date
    SUM("CONTRACT"."payment") AS Total_Payment, -- Sum up payments
    COALESCE(SUM(CASE WHEN strftime('%Y', "order_printing_house"."delivery date") = strftime('%Y', "contributes"."payment_date") 
                      THEN "order_printing_house"."cost" 
                      ELSE 0 END), 0) AS Total_Printing_Cost, -- Sum printing costs for the same year
	 SUM("CONTRACT"."payment") + 
    COALESCE(SUM(CASE WHEN strftime('%Y', "order_printing_house"."delivery date") = strftime('%Y', "contributes"."payment_date") 
                      THEN "order_printing_house"."cost" 
                      ELSE 0 END), 0) AS Combined_Cost -- Add partner payments and printing costs
FROM "CONTRACT"
JOIN "contributes" 
    ON "CONTRACT"."Partner_Tax_Id" = "contributes"."Partner_TaxId"
    AND "CONTRACT"."Publication-isbn" = "contributes"."Publication-isbn"
LEFT JOIN "order_printing_house" 
    ON strftime('%Y', "order_printing_house"."delivery date") = strftime('%Y', "contributes"."payment_date")
WHERE "contributes"."payment_date" IS NOT NULL -- Only include rows with non-NULL payment_date
GROUP BY Year
ORDER BY Year;
