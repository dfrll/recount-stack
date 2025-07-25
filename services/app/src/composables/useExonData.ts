import axios from 'axios'

export function useExonData() {

    async function fetchExon(projectId: string, startRow: number, endRow: number) {
        console.log('[useExonData] Fetching exon data for project:', projectId, 'rows:', startRow, '-', endRow)
        try {
            const res = await axios.get(`/api/project/${projectId}/exon`, {
                params: { start: startRow, end: endRow }
            })
            console.log('[useExonData] API response:', res.data)
            if (res.data.status == 'success') {
                return {
                    rows: res.data.table,
                    totalCount: res.data.totalCount
                }
            } else {
                console.error('[useExonData] API returned error status:', res.data)
                return { rows: [], totalCount: 0 }
            }

        } catch (e) {
            console.error('Failed to fetch exon data:', e)
            return { rows: [], totalCount: 0 }
        }
    }

    return { fetchExon }
}
