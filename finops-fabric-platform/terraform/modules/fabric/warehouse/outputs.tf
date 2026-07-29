output "warehouseId" {

  value = fabric_warehouse.this.id

}


output "warehouseName" {

  value = fabric_warehouse.this.display_name

}


output "warehouseConnectionString" {

  value = fabric_warehouse.this.properties.connection_string

}