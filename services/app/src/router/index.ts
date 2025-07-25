import { createRouter, createWebHistory } from 'vue-router'

const ProjectsPage = () => import('@/pages/ProjectsPage.vue')
const ProjectDetailsPage = () => import('@/pages/ProjectDetailsPage.vue')

const routes = [
    { path: '/projects', component: ProjectsPage },
    { path: '/project/:project_id', component: ProjectDetailsPage }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
