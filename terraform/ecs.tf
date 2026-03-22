resource "aws_ecs_cluster" "main" {
  name = "new-excel-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "new-excel-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" 
  memory                   = "512" 
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name      = "website"
    image     = "575894693774.dkr.ecr.ap-south-1.amazonaws.com/new_excel_engineering:latest"
    portMappings = [{
      containerPort = 80
      hostPort      = 80
    }]
  }])
}

resource "aws_ecs_service" "main" {
  name            = "new-excel-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = aws_subnet.public[*].id
    assign_public_ip = true
    security_groups  = [aws_security_group.ecs_tasks.id]
  }
}