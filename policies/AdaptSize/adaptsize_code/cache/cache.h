#ifndef CACHE_H
#define CACHE_H

#include <map>
#include <iostream>
#include <string>
#include <vector>
#include <cstdint>
#include <memory>
#include "request.h"




    class Cache;

    class Cache {
    public:
        // create and destroy a cache
        Cache()
                : _cacheSize(0),
                  _currentSize(0) {
        }

        virtual ~Cache() = default;

        // main cache management functions (to be defined by a policy)
        virtual bool lookup(const SimpleRequest &req) = 0;
        // check whether an object in a cache. Not update metadata
        virtual bool exist(const int64_t &key) {
            return false;
        }

        virtual void admit(const SimpleRequest &req) = 0;

        // configure cache parameters
        virtual void setSize(const uint64_t &cs) {
            _cacheSize = cs;
            //delay eviction because not all algorithms implement such interface
//        while (_currentSize > _cacheSize) {
//            evict();
//        }
        }



        virtual void update_stat_periodic() {
        }

        virtual size_t memory_overhead() {
            return sizeof(Cache);
        }

        uint64_t getCurrentSize() const {
            return (_currentSize);
        }

        uint64_t getSize() const {
            return (_cacheSize);
        }

        // basic cache properties
        uint64_t _cacheSize; // size of cache in bytes
        uint64_t _currentSize; // total size of objects in cache in bytes


    };

#endif /* CACHE_H */
