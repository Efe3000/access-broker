package authz

default decision := "deny"

decision := "allow" if {
    input.path == "/health"
}

decision := "allow" if {
    input.path == "/records"
    input.scope == "records:read"
}

decision := "requires_approval" if {
    input.path == "/delete-records"
    input.scope == "records:read"
}