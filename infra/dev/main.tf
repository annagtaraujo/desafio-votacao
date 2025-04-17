resource "kubernetes_namespace" "dev" {
  metadata {
    name = "dev"
  }
}

resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
  }
}

resource "kubernetes_namespace" "test" {
  metadata {
    name = "test"
  }
}

# -----------------------------------------------
# SERVICE ACCOUNT : AUTENTICAÇÃO DO
# GITHUB NO MINIKUBE
# -----------------------------------------------

resource "kubernetes_service_account" "github-sa" {
  metadata {
    name      = "github-sa"
    namespace = "kube-system"
  }
}

# -----------------------------------------------
# CLUSTER ROLE BINDING: ELE SERÁ NECESSÁRIO PARA 
# PERMITIR O ACESSO DO GITHUB AO MINIKUBE
# -----------------------------------------------

resource "kubernetes_cluster_role_binding" "github-admin-binding" {
  metadata {
    name = "github-admin-binding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-admin"
  }
  subject {
    kind      = "ServiceAccount"
    name      = "github-sa"
    api_group = "" # o valor "rbac.authorization.k8s.io" está implicito nessa sintaxe
    namespace = "kube-system"
  }
}