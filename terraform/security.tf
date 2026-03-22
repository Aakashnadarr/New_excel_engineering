# 1. The Security Group (The Firewall)
resource "aws_security_group" "ecs_tasks" {
  name        = "new-excel-sg"
  description = "Allow inbound access on port 80 and all outbound"
  vpc_id      = aws_vpc.main.id

  # Inbound Rules: Who can visit the website?
  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"] # This allows ANYONE on the internet to see the site
  }

  # Outbound Rules: Can the container talk to the internet?
  # (Crucial for pulling images from ECR and installing updates)
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "new-excel-sg"
  }
}

# 2. EKS Cluster Security Group (Optional but good practice)
resource "aws_security_group" "eks_cluster" {
  name        = "new-excel-eks-cluster-sg"
  description = "Cluster communication with worker nodes"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "new-excel-eks-sg"
  }
}