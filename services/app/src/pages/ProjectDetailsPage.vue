<script setup lang="ts">
import { useRoute } from 'vue-router'
import { ref, inject, watch, computed } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import { useVisibility } from '@/composables/useVisibility'
import { useProjectData } from '@/composables/useProjectData'
import { projectColumnDefs } from '@/columns/projectColumns'
import { useGeneData } from '@/composables/useGeneData'
import { geneColumnDefs } from '@/columns/geneColumns'
import type { GridApi, GridOptions, IServerSideDatasource, Theme } from 'ag-grid-community'

const route = useRoute()
const mdTheme = inject<Theme<unknown>>('mdTheme');

const gridApi = ref<GridApi | null>(null)
const geneGridApi = ref<GridApi | null>(null)

// composables
const { project, fetchProject } = useProjectData()
const { fetchGene } = useGeneData()
const { isVisible: isGeneVisible, toggle: toggleGene } = useVisibility(false)
const { isVisible: isProjectVisible, toggle: toggleProject } = useVisibility(true)

// computed properties
const projectId = computed(() => route.params.project_id as string)

// server-side datasource for gene table
const geneDatasource: IServerSideDatasource = {
    getRows(params: any) {
        const { startRow, endRow } = params.request;
        const currentProjectId = projectId.value

        console.log('[GeneDatasource] Fetching rows:', { startRow, endRow, projectId: currentProjectId })

        if (!currentProjectId) {
            console.error('[GeneDatasource] No project ID available')
            params.fail()
            return
        }

        fetchGene(currentProjectId, startRow, endRow)
            .then(({ rows, totalCount }) => {
                console.log('[GeneDatasource] Success:', {
                    projectId: currentProjectId,
                    rowCount: rows?.length,
                    totalCount,
                    firstRowData: rows?.[0],
                })
                params.success({ rowData: rows, rowCount: totalCount })
            })
            .catch((error) => {
                console.error('[GeneDatasource] Error fetching data:', error)
                params.fail()
            })
    },
}

// handlers
function onProjectGridReady(params: any) {
    gridApi.value = params.api
}

function onGeneGridReady(params: any) {
    geneGridApi.value = params.api
    console.log('[GeneGrid] Grid ready, setting datasource')

    // Set the datasource when grid is ready
    if (projectId.value) {
        params.api.setGridOption('serverSideDatasource', geneDatasource)
    }
}

// watchers
watch(
    projectId,
    async (newId) => {
        console.log('[Watch] Project ID changed:', newId)
        if (newId) {
            await fetchProject(newId)

            // Update gene grid datasource when project changes
            if (geneGridApi.value) {
                console.log('[Watch] Updating gene grid datasource')
                geneGridApi.value.refreshServerSide({ purge: true })
            }
        }
    },
    { immediate: true }
);

// grid options
const BASE_GRID_OPTIONS: GridOptions = {
    defaultColDef: {
        sortable: true,
        filter: true,
        resizable: true,
        wrapText: false,
        autoHeight: false,
    },
    pagination: true,
    animateRows: false,
}

const projectGridOptions: GridOptions = {
    ...BASE_GRID_OPTIONS,
    columnDefs: projectColumnDefs,
    rowModelType: 'clientSide',
    onGridReady: onProjectGridReady,
}

const geneGridOptions: GridOptions = {
    ...BASE_GRID_OPTIONS,
    columnDefs: geneColumnDefs,
    rowModelType: 'serverSide',
    onGridReady: onGeneGridReady,
}

</script>

<template>

    <button class="collapsible" @click="toggleProject">
        {{ isProjectVisible ? 'Metadata Table' : 'Metadata Table' }}
    </button>

    <div class="content" :style="{ display: isProjectVisible ? 'block' : 'none' }">
        <AgGridVue class="ag-theme-balham ag-grid-wrapper" :rowData="project" :gridOptions="projectGridOptions"
            :theme="mdTheme" />
    </div>

    <button class="collapsible" @click="toggleGene">
        {{ isGeneVisible ? 'Gene Table' : 'Gene Table' }}
    </button>

    <div class="content" :style="{ display: isGeneVisible ? 'block' : 'none' }">
        <AgGridVue class="ag-theme-balham ag-grid-wrapper" :gridOptions="geneGridOptions" :theme="mdTheme" />
    </div>

</template>

<style scoped>
.collapsible {
    background-color: #eee;
    color: #444;
    cursor: pointer;
    padding: 10px;
    width: 80vw;
    border: none;
    text-align: left;
    outline: none;
    font-size: 16px;
    margin-top: 1rem;
}

.active,
.collapsible:hover {
    background-color: #ccc;
}

.content {
    display: none;
    overflow: hidden;
    transition: max-height 0.2s ease-out;
}

.ag-grid-wrapper {
    height: 50vh;
    width: 80vw;
}
</style>
