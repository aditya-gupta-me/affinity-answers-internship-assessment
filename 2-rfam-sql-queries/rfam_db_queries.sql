/*
Question a) Taxonomy and Tiger Data
- How many types of tigers can be found in the taxonomy table of the dataset?
- What is the ncbi_id of the Sumatran Tiger?
(Hint: Use the biological name of the tiger)
*/

-- Query / Answer:  (Eight Tigers)
SELECT COUNT(*) AS Tiger_Strength 
FROM taxonomy 
WHERE species LIKE '%Panthera tigris%';

-- Query / Answer: ncbi_id -> 9695
SELECT ncbi_id AS Sumatran_Tiger_ncbi_id
FROM taxonomy 
WHERE species LIKE '%Panthera tigris sumatrae%';



/*
Question b) Table Relationships
- Find all the columns that can be used to connect the tables in the given database.
*/

-- Answer: Based on the Rfam schema and example queries, the tables are connected through the following key columns:

-- Main foreign-key relationships: (see below)
-- taxonomy.ncbi_id        = rfamseq.ncbi_id
-- rfamseq.rfamseq_acc     = full_region.rfamseq_acc
-- family.rfam_acc         = full_region.rfam_acc

-- Additional clan-level relationships: (see below):
-- family.rfam_acc         = clan_membership.rfam_acc
-- clan.clan_acc           = clan_membership.clan_acc



/*
Question c) Rice DNA Sequence
- Which type of rice has the longest DNA sequence?
(Hint: Use the rfamseq and taxonomy tables)
*/


SELECT t.species, t.ncbi_id, MAX(rf.length) as max_length
FROM taxonomy t
JOIN rfamseq rf ON t.ncbi_id = rf.ncbi_id
WHERE t.species LIKE '%Oryza%'  -- Oryza scientific genus of rice
GROUP BY t.species, t.ncbi_id
ORDER BY max_length DESC
LIMIT 1;


/*
Question d) Pagination Query
- Paginate a list of family names and their longest DNA sequence lengths (descending order)
- Only include families with DNA sequence lengths > 1,000,000
- Return the 9th page when there are 15 results per page
(Hint: Include family accession ID, family name, and maximum length)
*/

SELECT
    f.rfam_acc,
    f.rfam_id AS family_name,
    MAX(rf.length) AS max_length
FROM family f
JOIN full_region fr ON f.rfam_acc = fr.rfam_acc
JOIN rfamseq rf ON fr.rfamseq_acc = rf.rfamseq_acc
GROUP BY f.rfam_acc, f.rfam_id
HAVING MAX(rf.length) > 1000000
ORDER BY max_length DESC
LIMIT 15 OFFSET 120;