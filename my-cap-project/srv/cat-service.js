
const cds = require('@sap/cds');
const axios = require('axios');

module.exports = async function (srv) {
    // Handler for the 'READ' event of PopulationData
    srv.on('READ', 'PopulationData', async (req) => {
        try {
            // Fetch data from the external API
            const response = await axios.get('https://datausa.io/api/data?drilldowns=Nation&measures=Population');

            // Map API response to the entity structure
            return response.data.data.map(item => ({
                "ID Nation": item["ID Nation"],
                Nation: item.Nation,
                "ID Year": item["ID Year"],
                Year: item.Year,
                Population: item.Population,
                "Slug Nation": item["Slug Nation"]
            }));
        } catch (error) {
            req.error(500, `Error fetching data: ${error.message}`);
        }
    });
};

