import { ref } from 'vue'
import axios from 'axios'

export function useProjectData() {
    const project = ref<any[]>([])

    async function fetchProject(projectId: string) {
        try {
            const res = await axios.get(`/api/project/${projectId}`)
            project.value = res.data.status === 'success' ? res.data.table : []
        } catch (e) {
            console.error('Failed to fetch project data:', e)
            project.value = []
        }
    }

    return { project, fetchProject }
}
