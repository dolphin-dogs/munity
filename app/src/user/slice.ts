import { Workspace } from '../workspaces/slice';
import { createSlice } from '@reduxjs/toolkit';
import { sliceFactory } from '../factory/slice';

export interface User {
    created: Date,
    email: string,
    first_name: string,
    generic_groups: string[],
    id: string,
    is_superuser: boolean,
    last_name: string,
    modified: Date,
    roles: string[],
    username: string,
    workspace: Workspace | null
}

export interface UserState {
    userInEdition: User | null
}

export const initialState: UserState = {
    userInEdition: null
}

export const userSlice = createSlice({
    name: 'user',
    initialState,
    reducers: {
        setUserInEdition: (state, payload:{payload:User|null}) => {
            state.userInEdition = payload.payload;
        }
    }
});

export const userAPISlice = sliceFactory<User>({
    reducerName: 'userAPI',
    endpoint: '/users/',
    name: 'User'
});


export default userSlice.reducer;
export const { setUserInEdition } = userSlice.actions

export const {
    useGetUsersQuery,
    useGetUserQuery,
    useDeleteUserMutation,
    useUpdateUserMutation,
    useCreateUserMutation,
} = userAPISlice

