# 1. The Cluster Name (Needed for the 'update-kubeconfig' command)
output "cluster_name" {
  description = "The name of the EKS cluster"
  value       = aws_eks_cluster.main.name
}

# 2. The Cluster Endpoint (The URL kubectl talks to)
output "cluster_endpoint" {
  description = "The endpoint for your EKS Kubernetes API"
  value       = aws_eks_cluster.main.endpoint
}

# 3. The Region (To remind you which region you're in)
output "region" {
  description = "AWS region"
  value       = var.region
}

# 4. The VPC ID (Useful if you need to add a Database later)
output "vpc_id" {
  description = "The ID of the VPC created"
  value       = aws_vpc.main.id
}

# 5. Security Group ID
output "security_group_id" {
  description = "The ID of the security group for the pods"
  value       = aws_security_group.ecs_tasks.id
}