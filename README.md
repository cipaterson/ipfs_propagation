# Project Title

Test how long a file takes to propagate across the IPFS network.

## Description

This tool adds a file to an IPFS node and then times how long it takes to be available at several
IPFS gateways.

## Getting Started

### Dependencies

Just the packages in requirements.txt

If you are using an Infura account, then you must create a .env file with your Project ID and Project Secret. See ```env.example``` for details.

### Installing

```python
git clone <this repo>
cd ipfs_propergation
pip -r requirements.txt
```

### Executing program

Upload one file (to Infura by default) and time it's propagation to several IPFS gateways:
```
./ipfs_prop.py -c1
```
Upload many files to local IPFS node and time propagation:
```
./ipfs_prop.py http://localhost:5001
```

## Help

```
./ipfs_prop.py --help
```

## Authors

[Chris Paterson](https://github.com/cipaterson)

## Version History


## License

This project is in the public domain.

## Acknowledgments

