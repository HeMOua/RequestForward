export function invokeAddGroup(data: Partial<CreateGroupDto>): Promise<ApiResponse<number>> {
  return window.electron.ipcRenderer.invoke('group:create', data)
}

export function invokeGetAllGroups(): Promise<ApiResponse<Group[]>> {
  return window.electron.ipcRenderer.invoke('group:findAll')
}

export function invokeGetGroupById(id: number): Promise<ApiResponse<Group | undefined>> {
  return window.electron.ipcRenderer.invoke('group:findById', id)
}

export function invokeUpdateGroup(
  id: number,
  data: Partial<CreateGroupDto>
): Promise<ApiResponse<number>> {
  return window.electron.ipcRenderer.invoke('group:update', id, data)
}

export function invokeDeleteGroup(id: number): Promise<ApiResponse<number>> {
  return window.electron.ipcRenderer.invoke('group:delete', id)
}

export default {
  invokeAddGroup,
  invokeGetAllGroups,
  invokeGetGroupById,
  invokeUpdateGroup,
  invokeDeleteGroup
}
