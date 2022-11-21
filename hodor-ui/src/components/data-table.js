import { useMemo } from 'react';
import { DataGrid, gridClasses } from '@mui/x-data-grid';


export default function DataTable({ columns, rows, rowCount, page, pageSize, setPage, setPageSize }) {

    return (
        <div style={{ height: 650, width: '100%' }}>
            <DataGrid
                rows={rows}
                columns={columns}
                rowCount={rowCount}
                pageSize={pageSize}
                page={page}
                rowsPerPageOptions={[20]}
                checkboxSelection={false}
                paginationMode='server'
                onPageChange={(newPage) => setPage(newPage)}
                onPageSizeChange={(newPageSize) => setPageSize(newPageSize)}
                getRowHeight={() => 'auto'}
                sx={{
                    [`& .${gridClasses.cell}`]: {
                        py: 1,
                    },
                }}
            />
        </div>
    );
}
