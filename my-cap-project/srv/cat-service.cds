// service CatalogService {
//     @path: '/odata/v4/catalog'
//     entity PopulationData {
//         ID_Nation : String;      // Renamed from "ID Nation" to ID_Nation
//         Nation : String;
//         ID_Year : Integer;       // Renamed from "ID Year" to ID_Year
//         Year : String;
//         Population : Integer;
//         Slug_Nation : String;    // Renamed from "Slug Nation" to Slug_Nation
//     }
// }


using my.cap.project as db;

service CatalogService {
    @path: '/odata/v4/catalog'
    entity PopulationData as projection on db.PopulationData;
}
