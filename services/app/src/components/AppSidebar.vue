<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { SquareStack, Binoculars } from 'lucide-vue-next';
import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar"

const STORAGE_KEY = 'recountLabProjectIds'

// load persisted project IDs from sessionStorage (or empty array)
const persistedProjectIds = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '[]')

// reactive array to hold all project IDs clicked this session
const projectIds = ref<string[]>(persistedProjectIds)

const route = useRoute()

// watch route changes — add project_id if on /project/:project_id
watch(() => route.params.project_id, (newId) => {
    if (newId && !projectIds.value.includes(newId as string)) {
        projectIds.value.push(newId as string)
    }
})

// save changes to sessionStorage anytime projectIds changes
watch(projectIds, (newVal) => {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(newVal))
}, { deep: true })

// base items + persisted project IDs
const items = computed(() => {
    const baseItems = [
        { title: 'Projects', url: '/projects', icon: SquareStack },
    ]

    // add all persisted project IDs to sidebar items
    const projectItems = projectIds.value.map(id => ({
        title: id,
        url: `/project/${id}`,
        icon: Binoculars,
    }))

    return [...baseItems, ...projectItems]
})


</script>

<template>
    <Sidebar>
        <SidebarContent>
            <SidebarGroup>
                <SidebarGroupLabel>Recount Lab</SidebarGroupLabel>
                <SidebarGroupContent>
                    <SidebarMenu>
                        <SidebarMenuItem v-for="item in items" :key="item.title">
                            <SidebarMenuButton asChild>
                                <router-link :to="item.url" class="sidebar-link">
                                    <component :is="item.icon" class="sidebar-link"></component>
                                    <span>{{ item.title }}</span>
                                </router-link>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    </SidebarMenu>
                </SidebarGroupContent>
            </SidebarGroup>
        </SidebarContent>
    </Sidebar>
</template>
