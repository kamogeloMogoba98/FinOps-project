output "lakehouseId" {
  value = fabric_lakehouse.this.id
}

output "lakehouseName" {
  value = fabric_lakehouse.this.display_name
}

output "sqlEndpoint" {
  value = fabric_lakehouse.this.properties.sql_endpoint_properties.connection_string
}