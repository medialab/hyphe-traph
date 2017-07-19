# Notes

## Possible debug nightmare:

Before writing a node's data, one should ensure that the reference's data is not obsolete in case code between the node retrieval and the write did edit the binary data.
