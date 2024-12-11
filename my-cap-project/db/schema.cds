namespace my.cap.project;

entity PopulationData {
    ID_Nation : String(10);     // Shortened for SAP HANA constraints
    Nation : String(100);
    ID_Year : Integer;
    Year : String(4);
    Population : Integer;
    Slug_Nation : String(100);
}
